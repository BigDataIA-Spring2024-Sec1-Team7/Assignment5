# Assignment5

## Problem Statement

In this assignment, the primary goal is to investigate various prompting techniques to generate and analyze questions and answers. The process involves utilizing data retrieved from Snowflake, summarizing it using OpenAI, and storing the summarized data in Pinecone, an embedding database.

1. Exploration of Prompting Techniques: The assignment begins with an exploration of different techniques for generating questions and answers. These techniques could involve using different prompts or approaches to elicit responses from OpenAI's language model.

2. Data Fetching from Snowflake: Data is fetched from Snowflake, a cloud-based data warehousing platform. This data could be related to any domain or topic of interest for the assignment.

3. Summarization using OpenAI: The fetched data is then summarized using OpenAI's natural language processing capabilities. This step aims to condense the information into concise summaries that capture the key points or insights.

4. Storage in Pinecone: The summarized data, along with any associated metadata, is stored in Pinecone. Pinecone is utilized for its efficient storage and retrieval of embeddings, which are high-dimensional representations of the summarized data.

Overall, the assignment focuses on experimenting with different techniques for generating questions and answers, leveraging data from Snowflake, summarizing it using OpenAI, and storing the summarized data in Pinecone. The ultimate objective is to evaluate the effectiveness of these prompting techniques and their impact on question-answer generation and analysis.




## Codelab Link
[https://codelabs-preview.appspot.com/?file_id=1c6VB_qFBEqGw-6wcCtZOCc7Rcjyu1rTKkr46DdrcOcI#0](https://codelabs-preview.appspot.com/?file_id=14qlZ-2gF3lOy6qI_J2EucJKMsOx5OkMx6IVQOowjH_o#0)


## Project Goals


The objective of this assignment is to explore and evaluate different prompting techniques for generating and analyzing questions and answers using data fetched from Snowflake, summarized using OpenAI, and stored in Pinecone. The assignment consists of multiple steps:

Step 1:
- Fetch data from Snowflake.
- Summarize the fetched data using OpenAI.
- Chunk the summarized data.
- Embed the chunked data.
- Store the embedded data in Pincone.

Step 2:
a) Fetch data from Snowflake and generate 50 questions and answers using OpenAI GPT.
- Separate each question and answer.
- Create embeddings for each question-answer pair.
- Store the embeddings in Pincone, referring to this set as "Set A" questions and answers.

b) Utilize a sample PDF and the data from Snowflake to create prompts.
- Generate 50 questions and answers using OpenAI GPT based on the prompts.
- Refer to this set as "Set B" questions and answers.

Step 3:
- Utilize "Set B" questions and answers.
- Conduct a similarity search on the embeddings stored in Pinecone, specifically targeting "Set A."
- Retrieve the three most similar questions from "Set A."
- Find the corresponding answers to these similar questions.

Step 4:
- Utilize "Set A" and "Set B" questions and answers.
- Conduct a similarity search on the embeddings stored in Step 1.
- Compare the answers for all 50 questions in "Set A" and 50 questions in "Set B."
- Generate a comprehensive report detailing the similarities and differences between the answers obtained using the different prompting techniques.

This assignment aims to investigate the effectiveness of different prompting techniques in generating and analyzing questions and answers. It involves utilizing advanced natural language processing techniques and leveraging Snowflake, OpenAI GPT, Pinecone, and embeddings to achieve the desired outcomes. The ultimate goal is to provide insights into the strengths and limitations of each prompting approach and their impact on question-answer generation and analysis.


## Data Sources

1. Snowflake: Snowflake is the primary data source from which data needs to be fetched. Snowflake is a cloud-based data warehousing platform that allows users to store and analyze large amounts of structured and semi-structured data. In this assignment, Snowflake likely contains the raw data that needs to be summarized and analyzed.

2. OpenAI: OpenAI's GPT model is used for generating questions and answers based on the data fetched from Snowflake. OpenAI provides natural language processing models that can generate human-like text based on given prompts. In this assignment, OpenAI's GPT model is used to generate questions and answers.

3. Sample PDF: A sample PDF is mentioned in Step 2b of the assignment, which is utilized along with the data from Snowflake to create prompts for generating questions and answers using OpenAI GPT. This PDF likely contains additional information or context that can be used to generate relevant prompts.

4. Pinecone: Pinecone is used to store the embeddings of the summarized data, as well as the embeddings of the questions and answers generated using OpenAI GPT. Pinecone is a vector database that enables fast similarity searches and efficient storage and retrieval of vector data. In this assignment, Pinecone is used to store and retrieve embeddings for similarity searches.


## Technologies used
Streamlit, Snowflake, OpenAI, Pinecone


## Architecture Diagram
![data_pipeline_architecture](![assignment_5](https://github.com/BigDataIA-Spring2024-Sec1-Team7/Assignment5/assets/113384021/49580cbf-d92c-43e0-8210-4842803d4f4d)



## Pre-requisites

Before running this project, ensure you have the following prerequisites installed:

- [Python 3](https://www.python.org/downloads/): This project requires Python 3 to be installed. You can download and install Python 3 from the official Python website.


## How to run application locally

#### Creating Virtual Environment
1. Create a virtual environment using the command `python -m venv <name of virtual env>`. 
2. Install dependencies required to run the project using `pip install -r path/to/requirements.txt`
3. Activate created virtual env by running `source <name of virtual env>/bin/activate`


##### How to run
1. Create virtual environment and activate it
2. create a .env file to add the credentials required to connect with snowflake, Pinecone API Key, OpenAI API Key and AWS S3 bucket credentials. The required fields are the following
a. PINECONE_API_KEY = Pinecone API Key
b. OPENAI_API_KEY= OpenAI API Key
c. SNOWFLAKE_USER= Snowflake user id
d. SNOWFLAKE_PASSWORD= Snowflake passsword
e. SNOWFLAKE_ACCOUNT= Snowflake accout id
f. SNOWFLAKE_WAREHOUSE= Snwoflake Warehouse
g. SNOWFLAKE_DATABASE= Snowflake Database
h. SNOWFLAKE_SCHEMA= Snowflake schema
i. AWS_ACCESS_KEY_ID = AWS Access key
j. AWS_SECRET_ACCESS_KEY = Aws Secret access key
k. S3_BUCKET_NAME = S3 bucket name

3. Install Requirements.txt file
```
pip install -r Requirements.txt
```

4. Run partA, partB, partC and partD in the same order
```
python partA
python partB
python partC
python partD
```
5. After generating and loading vectors, will run streamlit app for frontend
```
streamlit run app.py
```

#### Docker


##### How to run
1. Pull the image from docker HUB

```sh
docker pull grobid/grobid:0.8.0
```

2. This will create the grobid image and pull in the necessary dependencies.
Here, we are using 0.8.0 version of Grobid.

3. Once done, run the Docker image and map the port to whatever you wish on
your host. We simply map port 8070 of the host to
port 8070 of the Docker :

```sh
docker run --rm --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0
```

4. Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8070
```

## References

[PyPdf](https://pypdf2.readthedocs.io/en/3.0.0/): PyPDF2 is a free and open source pure-python PDF library capable of splitting, merging, cropping, and transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF files. PyPDF2 can retrieve text and metadata from PDFs as well.

[Pincone](https://pincone.readthedocs.io/en/latest/): Pinecone is an open-source Python library developed by OpenAI, designed to interact with and utilize the capabilities of the GPT (Generative Pre-trained Transformer) models. It offers an intuitive interface for fine-tuning, generating text, and performing various natural language processing tasks using OpenAI's GPT models. Pincone provides functionalities for text generation, completion, summarization, and more, making it a versatile tool for researchers, developers, and enthusiasts working with natural language understanding and generation tasks.

[OpenAI GPT] (https://openai.com/gpt): OpenAI's GPT (Generative Pre-trained Transformer) is a state-of-the-art natural language processing model. It utilizes transformer architecture and is pre-trained on large text corpora to understand and generate human-like text. GPT models are capable of a wide range of language tasks, including text generation, completion, summarization, translation, and more. With its impressive performance and versatility, OpenAI's GPT has become a cornerstone in the field of natural language processing, empowering various applications in industries such as healthcare, finance, education, and entertainment.

[Snowflake] (https://www.snowflake.com/): Snowflake is a cloud-based data warehousing platform that allows organizations to store, manage, and analyze large volumes of structured and semi-structured data. It offers scalability, flexibility, and performance, enabling users to perform complex analytics and derive valuable insights from their data. Snowflake's architecture separates storage and compute, allowing users to scale each independently based on their requirements. With its built-in support for SQL and integration with popular BI tools, Snowflake simplifies data analytics workflows and empowers organizations to make data-driven decisions effectively.


## Learning Outcomes
- Exploration of Prompting Technique
- Data Fetching from Snowflake
- Summarization using OpenAI
- Storage in Pinecone

## Team Information and Contribution

| Name | Contribution % | Contribution |
| --- | --- | --- |
Asawari Kadam | 33.33% | Part 1 and streamlit |
Hariharan Sundaram | 33.33%  | Part 3 and Part 4|
Rutuja Kute | 33.33%  |  Part 2 and streamlit |


