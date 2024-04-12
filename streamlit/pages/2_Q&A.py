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
    question = st.text_input("Type your question here:")
    if st.button("Approach1 Answer"):
        if question:
            answer = partC.getAnswerForQuestion(question)
            st.write(answer)
        else:
            st.write("Please type a question first.")
    if st.button("Approach2 Answer"):
        if question:
            answer = partD.getAnswerForQuestion(question)
            st.write(answer)
        else:
            st.write("Please type a question first.")

# Calling the function to run the page
question_answer_page()

