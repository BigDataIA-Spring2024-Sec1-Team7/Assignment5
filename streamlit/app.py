import streamlit as st
import json

def main():
    st.title("CFA Questions Set A and Set B")
        # Button for resetting/clearing the displayed content
    if st.button("Reset"):
        # Clear the displayed content
        st.experimental_rerun()  # Rerun the app to clear the content
    # Button to fetch questions for Set B
    if st.button("Set A"):
            # Read the JSON file
        with open("OpenAIIntegrations/SetA_questions.json", "r") as json_file:
            data = json.load(json_file)

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
        # Read the JSON file
        with open("OpenAIIntegrations/SetB_questions.json", "r") as json_file:
            data = json.load(json_file)

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
