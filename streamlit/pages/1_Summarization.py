import streamlit as st


def generate_summary(topic):
    if topic == 'Applications of Financial Statement Analysis':
        with open("OpenAIIntegrations/Markdown_note_topic1.txt", "r") as text_file:
            data = text_file.read()
        return data


    elif topic == 'Analysis of Dividends and Share Repurchases':
        with open("OpenAIIntegrations/Markdown_note_topic2.txt", "r") as text_file:
            data = text_file.read()
        return data

    elif topic == 'Financial Analysis Techniques':
        with open("OpenAIIntegrations/Markdown_note_topic3.txt", "r") as text_file:
            data = text_file.read()
        return data

    else:
        return "Please select a topic."

st.title("Get Summary")

topic = st.selectbox("Select a topic:", [
    'Applications of Financial Statement Analysis',
    'Analysis of Dividends and Share Repurchases',
    'Financial Analysis Techniques'
])

if st.button("Summarize"):
    Notes = generate_summary(topic)
    st.write(Notes)