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


from partA import fetch_snowflake_data, perform_chunk_data, generate_openaidata

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
        
        question['options'] = options
        question['answer'] = answer
        
        questions.append(question)
       
    return questions



def build_markdown(snowflake_data_row):
    summary = snowflake_data_row
        # Generate technical note for each LOS
    technical_note = f"**Summary:**\n{summary}\n\n"
    return technical_note 

def buildPromptForQuestions_setA(context_data):
    # build our prompt with the retrieved contexts included
    prompt = (f"""You are given a paragraph. You must create 50 questions using it. Following are the rules -
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


def create_embeddings_and_upsert(questions):
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
    index.upsert(index_name=index_name, vectors=question_embedding_to_upsert, namespace="questions")
    index.upsert(index_name=index_name, vectors=answer_embedding_to_upsert, namespace="answers")

def generate_50_questions_setA():
    topic = 'Applications of Financial Statement Analysis'
    context_data=fetch_snowflake_data(topic)
    print("Snowflake data fetch complete")
    markdown_doc = build_markdown(snowflake_data_row=context_data)
    print("Markdown data generation complete")
    prompt = buildPromptForQuestions_setA(context_data= markdown_doc)
    print("Prompt building done")
#     question = """You are an exam helper who generates 50 questions along with four options and answer on the content given by user. \n
#     This should be the format of question: \n 1. Why are projections of future performance important in credit analysis?
#    A) To determine current stock prices
#    B) To evaluate a borrower's ability to repay debt
#    C) To assess management efficiency
#    D) To compare financial reporting standards
#    Answer: B) projections of future performance important in credit analysis to evaluate a borrower's ability to repay debt"""
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
    create_embeddings_and_upsert(questions)
    print("Question and answer embedding creation complete")

generate_50_questions_setA()


def buildPromptForQuestions_setB(context_data, pdf_data):
    # build our prompt with the retrieved contexts included
    prompt = (
        f"""You are given a paragraph. You must create 50 questions with four options. Each question can have only one right option and give your justifications on why you chose that answer.
        Multiple options cannot be correct and do not use "All of the above" option.
      
      Format of the question is as follows:
      1. Question?
      A) Option 1
      B) Option 2
      C) Option 3
      D) Option 4
      Answer: complete Option x with justification
      
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


def generate_50_questions_setB():
    topic = 'Applications of Financial Statement Analysis'
    context_data=fetch_snowflake_data(topic)
    markdown_doc = build_markdown(snowflake_data_row=context_data)
    local_file_path=get_pdf()
    pdf_data = extract_text_from_pdf(pdf_file_path=local_file_path)
    prompt = buildPromptForQuestions_setB(context_data= markdown_doc, pdf_data=pdf_data)
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

    print("JSON data has been stored to:", file_path)

generate_50_questions_setB()

