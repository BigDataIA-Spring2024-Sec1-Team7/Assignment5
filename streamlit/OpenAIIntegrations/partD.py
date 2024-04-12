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
import openai
import os

import string
import random
from PyPDF2 import PdfReader

import pinecone
import os
from pinecone import Pinecone

import json
from ast import literal_eval
from openai import OpenAI

load_dotenv()

# initialize connection to pinecone
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = 'summary-part1'

index = pinecone_client.Index(index_name)    
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _getEmbeddingsForQuestion(question, topic):
    embed_model = "text-embedding-3-small"
    question_embedding = openai_client.embeddings.create(
        input=question, model=embed_model
    ).data[0].embedding
    res = index.query(
        vector=question_embedding,
        top_k=3,
        include_values=False,
        namespace=('doc-summary-'+topic).replace(' ', '-')
    )
    idList = []
    for match in res.matches:
        idList.append(match.id)
    return idList

def _getContextFromMatchingKnowledgeEmbeddings(indexes, topic):
    res = index.fetch(ids=indexes, namespace=("doc-summary-"+topic).replace(' ', '-') )
    contextStr = ""
    for key, match in res.vectors.items():
        contextStr += match.metadata['text'] + "\n"
    return contextStr

def _fetchAnswerFromGPT(contextStr, question):
    prompt = f"""
                Following is the context paragraph:
                {contextStr}
                
                Answer the following question based on the above context. It has only one right choice. Justify your answer:
                {question}
            """
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful Question/Answer Bot. If the question cannot be answered with the given context reply 'I do not have an answer to it'"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Starting point
def getAnswerForQuestion(question, topic):
    matchingQuestionIndexes = _getEmbeddingsForQuestion(question, topic)
    print("Matching knowledge base paragraphs fetched from DB")
    contextStr = _getContextFromMatchingKnowledgeEmbeddings(indexes=matchingQuestionIndexes, topic=topic)
    print("Matching context built using knowledge fetched from DB")
    gptAnswer = _fetchAnswerFromGPT(contextStr, question)
    print("Found GPT answer\n")
    return gptAnswer

def _testWithQuestion(topic):
    # sample_question = """What role does understanding financial reporting standards play in financial statement analysis?
    #                   "It helps comparisons among different regulatory environments.\n   B) It simplifies the financial statements for non-expert readers.\n   C) It is only necessary for auditors and not investors.\n   D) It is beneficial for preparing tax returns."
    #               """
    gpt_answers_seta_approach1 = []
    gpt_answers_setb_approach1 = []
    questions_setb_file_path = './SetB_questions.json'
    questions_seta_file_path = './SetA_questions.json'
    
    # SETB
    # Open the file and load its contents
    with open(questions_setb_file_path, 'r') as json_file:
        data_list = json.load(json_file)
        for data in data_list:
            question = ""
            question += data['question'] + "\n" + ''.join(data['options'])
            gptAnswer = getAnswerForQuestion(question)
            gpt_answers_setb_approach1.append({'question': data['question'], 'options': data['options'], 'gpt_answer': gptAnswer})
    
    # Writing JSON data to a file
    with open('gpt_answers_setb_approach1.json', "w") as json_file:
        json.dump(gpt_answers_setb_approach1, json_file, indent=4)

    # SETA
    # Open the file and load its contents
    with open(questions_seta_file_path, 'r') as json_file:
        data_list = json.load(json_file)
        for data in data_list:
            question = ""
            question += data['question'] + "\n" + ''.join(data['options'])
            gptAnswer = getAnswerForQuestion(question)
            gpt_answers_seta_approach1.append({'question': data['question'], 'options': data['options'], 'gpt_answer': gptAnswer})
    
    # Writing JSON data to a file
    with open('gpt_answers_seta_approach1.json', "w") as json_file:
        json.dump(gpt_answers_seta_approach1, json_file, indent=4)


def main():
    topic='Applications of Financial Statement Analysis'
    _testWithQuestion(topic=topic)
    print("Stage 4 run successfully")

if __name__ == "__main__":
    main()
