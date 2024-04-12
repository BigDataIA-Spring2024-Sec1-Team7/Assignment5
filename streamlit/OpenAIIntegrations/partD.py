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


def _getEmbeddingsForQuestion(question):
    embed_model = "text-embedding-3-small"
    question_embedding = openai_client.embeddings.create(
        input=question, model=embed_model
    ).data[0].embedding
    res = index.query(
        vector=question_embedding,
        top_k=3,
        include_values=False,
        namespace='doc_summary'
    )
    idList = []
    for match in res.matches:
        idList.append(match.id)
    return idList

def _getContextFromMatchingKnowledgeEmbeddings(indexes):
    res = index.fetch(ids=indexes, namespace="doc_summary")
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
            {"role": "system", "content": "You are a helpful Question/Answer Bot"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Starting point
def getAnswerForQuestion(question):
    matchingQuestionIndexes = _getEmbeddingsForQuestion(question)
    print("Matching knowledge base paragraphs fetched from DB")
    contextStr = _getContextFromMatchingKnowledgeEmbeddings(matchingQuestionIndexes)
    print("Matching context built using knowledge fetched from DB")
    gptAnswer = _fetchAnswerFromGPT(contextStr, question)
    print("Found GPT answer\n")
    return gptAnswer

def _testWithQuestion():
    sample_question = """What role does understanding financial reporting standards play in financial statement analysis?
                      "It helps comparisons among different regulatory environments.\n   B) It simplifies the financial statements for non-expert readers.\n   C) It is only necessary for auditors and not investors.\n   D) It is beneficial for preparing tax returns."
                  """
    gptAnswer = getAnswerForQuestion(sample_question)
    print(gptAnswer)


def main():
    _testWithQuestion()
    print("Stage 4 run successfully")

if __name__ == "__main__":
    main()
