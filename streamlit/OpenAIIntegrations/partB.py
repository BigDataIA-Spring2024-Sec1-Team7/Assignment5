import snowflake.connector
import pinecone
from pinecone import Pinecone, PodSpec
from langchain.embeddings.openai import OpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv
import os
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from uuid import uuid4
from tqdm.auto import tqdm

import string
import random
from PyPDF2 import PdfReader

import boto3
from botocore.exceptions import NoCredentialsError
import os
from urllib.parse import urlparse
from pathlib import Path




import json

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import re



AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def get_pdf():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    local_folder_path="/tmp/sourcedata/"
    local_file_path="/tmp/sourcedata/level1_sample.pdf"
    Path(local_folder_path).mkdir(parents=True, exist_ok=True)
    s3_client.download_file(S3_BUCKET_NAME, "example_questions/level1_sample.pdf", "/tmp/sourcedata/level1_sample.pdf")
    return local_file_path

def parse_questions(input_string):
    questions = []
    
    # Split the input string into individual questions
    question_texts = re.split(r'\d+\.', input_string)
    # Remove the empty string at the beginning
    question_texts = question_texts[1:]
    
    for question_text in question_texts:
        question = {}
        
        print(question_text)
        print("**************************************")
        # Extract the question number
        match = re.match(r'^\s*(\d+)\.', question_text)
        if match:
            question['number'] = int(match.group(1))
        
        # Extract the question itself
        question['question'] = question_text.split('\n')[0].strip()
        
        # Extract options and answer
        options_and_answer = re.findall(r'([A-D]\))\s*(.*?)\s*(?=Answer:)', question_text, re.DOTALL)
        options = [o[1].strip() for o in options_and_answer]
        # Extract answer and justification
        answer_match = re.search(r'Answer:(.|\n)*', question_text)
        if answer_match:
            answer = answer_match.group(0)
        else:
            answer = None
        if(answer == None or len(options) == 0 or question['question'] == None):
            continue
        question['options'] = options
        question['answer'] = answer
        
        questions.append(question)
    return questions


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

def build_markdown(snowflake_data_row):
    summary = snowflake_data_row
        # Generate technical note for each LOS
    technical_note = f"**Summary:**\n{summary}\n\n"
    return technical_note 

def buildPromptForQuestions_setA(context_data, question_count):
    # build our prompt with the retrieved contexts included
    prompt = (f"""You are given a paragraph. You must create {question_count} questions using it. Following are the rules -
      1. Each question should have only 4 options
      2. There should always be only one correct answer
      3. Do not create "All of the above" option
      4. Question and answer should be formatted as: 
        1. Question?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: Option x with justification
      
    
    Below is the paragraph which you should use to build the questions:
     {context_data}"""  )
    return prompt



index_name = 'summary-part1'

api_key = os.getenv("PINECONE_API_KEY")

# initialize connection to pinecone
pinecone_client = Pinecone(api_key=api_key)

index = pinecone_client.Index(index_name)    


def create_embeddings_and_upsert(questions, topic):
    embed_model = "text-embedding-3-small"
    question_embedding_to_upsert= []
    answer_embedding_to_upsert= []
    for que in questions:
        complete_question = que['question'] + ','.join(que['options'])
        que_embeddings  = openai_client.embeddings.create(
        input=complete_question, model=embed_model
    )
        answer_embeddings  = openai_client.embeddings.create(
        input=que['answer'], model=embed_model
    )
        characters = string.ascii_letters + string.digits
        rand_chunk_code = ''.join(random.choices(characters, k=3))
        question_embedding_to_upsert.append({'id': f'doc-QA-{rand_chunk_code}', 'values': que_embeddings.data[0].embedding, 'metadata': {'text': complete_question} })
        answer_embedding_to_upsert.append({'id': f'doc-QA-{rand_chunk_code}', 'values': answer_embeddings.data[0].embedding, 'metadata': {'text': que['answer']} })
    index.upsert(index_name=index_name, vectors=question_embedding_to_upsert, namespace=("questions-"+topic).replace(' ', '-') )
    index.upsert(index_name=index_name, vectors=answer_embedding_to_upsert, namespace="answers-"+topic.replace(' ', '-') )


def generate_questions_setA(topic, question_count):
    context_data=fetch_snowflake_data(topic)
    print("Snowflake data fetch complete")
    markdown_doc = build_markdown(snowflake_data_row=context_data)
    print("Markdown data generation complete")
    prompt = buildPromptForQuestions_setA(context_data=markdown_doc, question_count=question_count)
    print("Prompt building done")
    question = "You are a question bank who generates questions and answers along with brief justifications"
    gpt_questions = generate_openaidata(prompt,question)
    print("GPT questions generation for set A done")
    questions = parse_questions(gpt_questions)
    print("Question and answer parsing complete")
    
    for quest in questions:
        print("-----------------")
        print(quest)

    file_path = "SetA_questions.json"

    # Writing JSON data to a file
    with open(file_path, "w") as json_file:
        json.dump(questions, json_file, indent=4)

    print("JSON data has been stored to:", file_path)
    return questions


def buildPromptForQuestions_setB(context_data, pdf_data, question_count):
    # build our prompt with the retrieved contexts included
    prompt = (f"""You are given a paragraph. You must create {question_count} questions using it. Following are the rules -
      1. Each question should have only 4 options
      2. There should always be only one correct answer
      3. Do not create "All of the above" option
      4. Question and answer should be formatted as: 
        1. Question?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: Option x with justification
      
      Below is the contextual data:
     {context_data} 

     You can refer these example questions for the level of difficulty\n" + {pdf_data}"""
    )
    return prompt

    

def extract_text_from_pdf(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    combined_text = ""
    for page in reader.pages:
        combined_text += page.extract_text()
    return combined_text


def generate_questions_setB(topic, question_count):    
    context_data=fetch_snowflake_data(topic)
    markdown_doc = build_markdown(snowflake_data_row=context_data)
    local_file_path=get_pdf()
    pdf_data = extract_text_from_pdf(pdf_file_path=local_file_path)
    prompt = buildPromptForQuestions_setB(context_data= markdown_doc, pdf_data=pdf_data, question_count=question_count)
    question = "You are a question bank who generates questions and answers along with brief justifications"
    gpt_questions = generate_openaidata(prompt,question)
    questions = parse_questions(gpt_questions)
    for quest in questions:
        print("-----------------")
        print(quest)

    file_path = "SetB_questions.json"

    # Writing JSON data to a file
    with open(file_path, "w") as json_file:
        json.dump(questions, json_file, indent=4)
    return questions


def main():
    question_count = 50
    topic = 'Financial Analysis Techniques'
    questions = generate_questions_setA(topic=topic, question_count=question_count)
    create_embeddings_and_upsert(questions=questions, topic=topic)
    print("Question and answer embedding creation complete for set A")
    generate_questions_setB(topic=topic, question_count=question_count)
    print("Stage 2 run successfully")

if __name__ == "__main__":
    main()