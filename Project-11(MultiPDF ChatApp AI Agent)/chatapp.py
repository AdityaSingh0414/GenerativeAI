import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            st.error(f"Error reading {pdf.name}: {str(e)}")
    return text


# Example Dry Run
# Maan lo:
# PDF 1
#   Page 1 → "Hello "
#   Page 2 → "World"
# PDF 2
#   Page 1 → "Python"
#
# Execution:
# text = ""
# PDF 1
#   Page 1 -> text = "Hello "
#   Page 2 -> text = "Hello World"
# PDF 2
#   Page 1 -> text = "Hello WorldPython"
# return "Hello WorldPython"


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


# RecursiveCharacterTextSplitter ek LangChain ka class hai jo bade text ko intelligently chhote parts me todta hai.
# chunk_size=50000
# Har chunk me maximum 50,000 characters honge.
# Agar text isse bada hoga to usko next chunk me divide kar diya jayega.
# chunk_overlap=1000
# Har naye chunk me pichle chunk ke last 1000 characters dobara include honge.
# Isse context lose nahi hota aur AI ko continuity samajhne me help milti hai.
#
# Original Text (1,20,000 characters)
#
# Chunk 1 : Character 1      → 50,000
# Chunk 2 : Character 49,001 → 99,000
# Chunk 3 : Character 98,001 → 1,20,000
#
# Notice:
#
# Chunk 2 starts from 49,001, not 50,001, because 1000 characters overlap hain.
# Isi tarah Chunk 3 bhi previous chunk ke last 1000 characters se start hota hai.


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


# Ye function text chunks ko embeddings me convert karta hai,
# unhe FAISS vector database me store karta hai, aur database ko
# local system par save kar deta hai.
#
# GoogleGenerativeAIEmbeddings Google Gemini ka embedding model load karta hai.
# "models/embedding-001" ek pretrained embedding model hai.
# Ye har text chunk ko numbers (vectors) me convert karta hai.


def get_conversation_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


# Ye function LLM (Gemini) aur Prompt Template ko use karke ek
# Question-Answer (QA) Chain banata hai. Jab user koi question
# poochta hai, to ye chain retrieved context aur question ko Gemini
# ko bhejkar answer generate karti hai.


def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    new_db = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    docs = new_db.similarity_search(user_question)

    chain = get_conversation_chain()
    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )

    print(response)
    st.write("Reply:", response["output_text"])


def main():
    st.set_page_config(page_title="Multi PDF Chatbot", page_icon=":scroll:")
    st.header("Multi-PDF's 📚 - Chat Agent 🤖 ")

    user_question = st.text_input("Ask a Question from the PDF Files uploaded .. ✍️📝")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.image("img/Robot.jpg")
        st.write("---")

        st.title("📁 PDF File's Section")
        pdf_docs = st.file_uploader(
            "Upload your PDF Files & \n Click on the Submit & Process Button ",
            accept_multiple_files=True
        )
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):  # user friendly message.
                raw_text = get_pdf_text(pdf_docs)  # get the pdf text
                text_chunks = get_text_chunks(raw_text)  # get the text chunks
                get_vector_store(text_chunks)  # create vector store
                st.success("Done")

        st.write("---")
        st.write("AI App created by @ Aditya Singh")  # add this line to display the image


if __name__ == "__main__":
    main()
