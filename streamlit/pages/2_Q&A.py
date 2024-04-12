import streamlit as st
import OpenAIIntegrations.partC as partC
import OpenAIIntegrations.partD as partD


# Function to get answer based on question
def get_answer(question):
    # Here you can implement your logic to generate an answer based on the question
    # For demonstration purposes, let's just return a simple response
    return "The answer to your question is: Hello, you asked '{}'".format(question)

def question_answer_page():
    st.title("Ask Questions")
    # Dropdown for topic
    topic = st.selectbox("Select a topic:", [
        'Applications of Financial Statement Analysis',
        'Analysis of Dividends and Share Repurchases',
        'Financial Analysis Techniques'
    ])
    question = st.text_input("Type your question here:")
    if st.button("Approach1 Answer"):
        if question:
            answer = partC.getAnswerForQuestion(question=question, topic=topic)
            st.write(answer)
        else:
            st.write("Please type a question first.")
    if st.button("Approach2 Answer"):
        if question:
            answer = partD.getAnswerForQuestion(question=question, topic=topic)
            st.write(answer)
        else:
            st.write("Please type a question first.")

# Calling the function to run the page
question_answer_page()

