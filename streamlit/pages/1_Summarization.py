import streamlit as st
import OpenAIIntegrations.partA as partA

def generate_summary(topic):
    return partA.generateGPTSummary(topic=topic)

st.title("Get Summary")

topic = st.selectbox("Select a topic:", [
    'Applications of Financial Statement Analysis',
    'Analysis of Dividends and Share Repurchases',
    'Financial Analysis Techniques'
])

if st.button("Summarize"):
    Notes = generate_summary(topic)
    st.write(Notes)