import streamlit as st
import json
import OpenAIIntegrations.partB as partB

def main():
    st.title("CFA Questions Set A and Set B")
    
    # Dropdown for topic
    topic = st.selectbox("Select a topic:", [
        'Applications of Financial Statement Analysis',
        'Analysis of Dividends and Share Repurchases',
        'Financial Analysis Techniques'
    ])
        # Button for resetting/clearing the displayed content
    if st.button("Reset"):
        # Clear the displayed content
        st.experimental_rerun()  # Rerun the app to clear the content
    # Button to fetch questions for Set A
    if st.button("Set A"):
        # Generate questions for part A
        data = partB.generate_questions_setA(topic=topic, question_count=10)
        print(data)
        # Display questions and answers
        for i, item in enumerate(data, start=1):
            st.header(f"Question {i}: {item['question']}")
            
            st.write("Options:")
            for option in item["options"]:
                st.write(option)
            
            st.write("Answer:")
            st.write(item["answer"])
            st.markdown("---")  # Add a horizontal line between questions

    if st.button("Set B"):
        # Generate questions for part A
        data = partB.generate_questions_setB(topic=topic, question_count=10)
        
        # Display questions and answers
        for i, item in enumerate(data, start=1):
            st.header(f"Question {i}: {item['question']}")
            
            st.write("Options:")
            for option in item["options"]:
                st.write(option)
            
            st.write("Answer:")
            st.write(item["answer"])
            st.markdown("---")  # Add a horizontal line between questions
    

if __name__ == "__main__":
    main()
