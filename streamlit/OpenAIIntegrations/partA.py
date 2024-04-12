import snowflake.connector
from pinecone import Pinecone, PodSpec
from langchain.embeddings.openai import OpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv
import os
import openai 
from langchain.text_splitter import RecursiveCharacterTextSplitter

from uuid import uuid4
from tqdm.auto import tqdm

import os

import string
import random

from openai import OpenAI

import pinecone
import os
from pinecone import Pinecone

load_dotenv()

import tiktoken

tokenizer = tiktoken.get_encoding('cl100k_base')

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)





# Step 1: Retrieve Learning Outcome Statements from Snowflake database
    # Connect to Snowflake
def fetch_snowflake_data(topic):
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
        )

        # Query learning outcome statements
    query = f"SELECT DISTINCT introduction, learning_outcomes, summary FROM web_Scraped_data WHERE topic='{topic}'"
    cursor = conn.cursor()
    cursor.execute(query)
    los_data = cursor.fetchone()
    conn.close()
    return los_data

def build_markdown(snowflake_data_row):
    introduction, learning_outcomes, summary = snowflake_data_row
        # Generate technical note for each LOS
    technical_note = f"**Introduction:** {introduction}\n\n" \
                            f"**Learning Outcomes:**\n{learning_outcomes}\n\n" \
                            f"**Summary:**\n{summary}\n\n"

    return technical_note



def buildPromptForSummarization(context_data):
    # build our prompt with the retrieved contexts included
    prompt = (
        "You are given contextual data containing overview, learning outcomes and summary. Create a detailed report of this "
        +"so it can be used by you later to answer questions on this document. Below is the contextual data: \n "+"Context:\n"+ context_data
    )
    return prompt


def generate_openaidata(initial_prompt, question):
   
    stream = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": question },
            {"role": "user", "content": initial_prompt}
        ],
        max_tokens=10000,
    stream=True,
    )
    text = ""
    for chunk in stream:
        # print(type(chunk.choices[0].delta))
        if chunk.choices[0].delta.content is not None:
            text = text + chunk.choices[0].delta.content
    return text

    


def perform_chunk_data(string_to_chunk):
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]
    )
    texts = text_splitter.split_text(string_to_chunk)
    chunks.extend([{
        'text': texts[i],
        'chunk': i,
    } for i in range(len(texts))])
    return chunks




# initialize openai API key


def create_embeddings(chunks):
    embed_model = "text-embedding-3-small"
    chunks_text_list = [chunk['text'] for chunk in chunks]
    embeddings_list = openai_client.embeddings.create(
        input=chunks_text_list, model=embed_model
    )
    return embeddings_list




def upsert_into_db(namespace: str, data_chunks, embeddings_list):
    embedding_to_upsert = []
    for i in range(0, len(data_chunks)):
        # Define the pool of characters to choose from
        characters = string.ascii_letters + string.digits
        # Generate a random combination of 3 characters
        rand_chunk_code = ''.join(random.choices(characters, k=3))
        embedding_to_upsert.append({'id': f'doc-summ-{rand_chunk_code}', 'values': embeddings_list.data[i].embedding, 'metadata': {'text': data_chunks[i]['text']} })

    index.upsert(index_name=index_name, vectors=embedding_to_upsert, namespace=namespace)

# Create pinecone index
index_name = 'summary-part1'

api_key = os.getenv("PINECONE_API_KEY")

# initialize connection to pinecone
pinecone_client = Pinecone(api_key=api_key)

def deleteAndCreatePineconeIndex():
    # check if index already exists (it shouldn't if this is first time)
    if len(pinecone_client.list_indexes()) > 0:
        pinecone_client.delete_index(name=pinecone_client.list_indexes()[0].name)

    # Create index
    pinecone_client.create_index(
        index_name,
        dimension=1536,
        metric='dotproduct',
        spec=PodSpec(
        environment="gcp-starter"
    ))

index = pinecone_client.Index(index_name)    



def stage1_summarization(topic):
    deleteAndCreatePineconeIndex()
    print("Deleted prev pinecone index and created new one")
    scraped_data_row = fetch_snowflake_data(topic)
    introduction, learning_outcomes, summary = scraped_data_row
    markdown_doc = build_markdown(snowflake_data_row=scraped_data_row)
    print("Building markdown complete")
    prompt = buildPromptForSummarization(context_data=markdown_doc)
    question ="You are an exam helper who generates detailed notes for future use to answer questions.Below is the provided content by user"
    print("Building prompt complete")
    gpt_summary = generate_openaidata(prompt,question)
    #to store markdown doc for selected topic
    file_path = "Markdown_note.txt"

    # Open the file in write mode and write the string to it
    with open(file_path, "w") as file:
        file.write(gpt_summary)
    print("Generation of context gpt summary complete")

    # Chunking and embedding of summarized note from chatgpt
    summary_chunks = perform_chunk_data(gpt_summary)
    print("Data chunking complete")
    embeddings_list = create_embeddings(summary_chunks)
    print("Embedding creation complete")
    upsert_into_db('doc_summary', summary_chunks, embeddings_list)
    print("Upsert into DB complete")
    # Chunking and embedding LOS data 
    summary_chunks = perform_chunk_data(learning_outcomes)
    print("Chunking complete")
    embeddings_list = create_embeddings(summary_chunks)
    print("Embedding creation complete")
    upsert_into_db('doc_summary', summary_chunks, embeddings_list)
    print("Upsert into DB complete")
    


def main():
    topic = 'Financial Analysis Techniques'
    stage1_summarization(topic)
    print("Stage 1 run successfully")

if __name__ == "__main__":
    main()