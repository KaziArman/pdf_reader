import streamlit as st
import fitz  # PyMuPDF
import re
from groq import Groq


client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def extract_abbreviation_context(full_text):
    """
    Finds abbreviations like (ABC) and returns context around them.
    """
    pattern = re.compile(r"\(([A-Z]{2,}[A-Za-z0-9]*)\)")
    contexts = []

    for match in pattern.finditer(full_text):
        start, end = match.span()
        left = max(0, start - 120)
        right = min(len(full_text), end + 120)
        snippet = full_text[left:right].replace("\n", " ")
        contexts.append(snippet)

    if not contexts:
        return full_text[:3000]

    return " ... ".join(contexts)

st.title("Python Project 2 – Web-Based LLM App (Groq Version)")
st.header("MSIS 5193 – Question 4 Redevelopment (Closed-Source LLM)")
st.subheader("Team Members")
st.text("""
- Chinmay Deshpande
- Dheerusha Tiwari
- Kazi Armaan Ahmed
- Siddharth Birajdar
""")

if "full_text" not in st.session_state:
    st.session_state.full_text = ""

st.markdown("## Upload PDF Document")

uploaded_file = st.file_uploader("Upload your PDF here:", type=["pdf"])

if st.button("Submit File for Context"):
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            text = ""
            for page in doc:
                text += page.get_text()

        st.session_state.full_text = text
        st.success(f"'{uploaded_file.name}' processed successfully!")
    else:
        st.warning("Please upload a PDF first.")

st.markdown("---")
st.markdown("## Generate Abbreviation Index")

if st.button("Generate Abbreviation Index"):
    if not st.session_state.full_text.strip():
        st.error("No document loaded. Upload a PDF first.")
    else:
        extracted = extract_abbreviation_context(st.session_state.full_text)

        prompt = f"""
Extract technical abbreviations AND their definitions from the text.

Rules:
1. Output format:
   * **ABC**: Full Meaning
2. Only include abbreviations that are DEFINED in the text.
3. Ignore author citations like (Smith, 2020).
4. Do NOT guess definitions.
5. If unclear, skip it.

Context:
{extracted}
"""

        with st.spinner("Generating abbreviation index..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You extract abbreviations and definitions."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_output = response.choices[0].message.content

        st.markdown("### Abbreviation Index")
        st.markdown(ai_output)


st.markdown("---")
st.header("Ask a Question About the Document")

question = st.text_input("Enter your question here:")

if st.button("Get AI Response"):
    if question.strip():
        if st.session_state.full_text.strip():
            context_part = st.session_state.full_text[:12000]

            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You answer questions strictly using the document."},
                        {"role": "user", "content": f"Context:\n{context_part}\n\nQuestion: {question}"}
                    ]
                )
                ai_msg = response.choices[0].message.content

            st.subheader("AI Response")
            st.write(ai_msg)

        else:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Answer the user's question."},
                        {"role": "user", "content": question}
                    ]
                )
                ai_msg = response.choices[0].message.content

            st.subheader("AI Response")
            st.write(ai_msg)
    else:
        st.warning("Please enter a question first.")
