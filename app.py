import streamlit as st
import fitz  # PyMuPDF
from groq import Groq


client = Groq(api_key=st.secrets["GROQ_API_KEY"])


st.title("Python Project 2 – Question 4")
st.header("Closed-Source LLM Redevelopment using Groq API")

st.write("Upload a document and ask a question. The Groq LLM will answer using the uploaded content as context.")

uploaded_file = st.file_uploader("Upload PDF or TXT file", type=["pdf", "txt"])
context = "" 

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    if uploaded_file.type == "application/pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        context = text

    elif uploaded_file.type == "text/plain":
        context = uploaded_file.read().decode("utf-8", errors="ignore")

    st.info("File processed successfully! You can now ask your question.")

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content


question = st.text_input("Enter your question:")

if st.button("Get AI Answer"):

    if context.strip() == "":
        st.error("⚠ Please upload a PDF/TXT file first.")
    else:
        final_prompt = f"""
You are given the following document content:

{context}

Now answer the user question: {question}
"""

        with st.spinner("Thinking..."):
            answer = ask_groq(final_prompt)

        st.subheader("AI Response")
        st.write(answer)

