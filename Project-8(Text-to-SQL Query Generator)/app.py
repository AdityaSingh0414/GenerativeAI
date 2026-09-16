import streamlit as st
from pipeline import run_pipeline

st.set_page_config(page_title="Text-to-SQL Generator", page_icon="🧠")
st.title("🧠 Text-to-SQL Query Generator")
st.caption("Ask a question in plain English about students, sales, or IPL matches.")

question = st.text_input("Your question:", placeholder="e.g. Which team won the most IPL matches?")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        result = run_pipeline(question)

    if result.get("sql"):
        st.subheader("Generated SQL")
        st.code(result["sql"], language="sql")

    if "rows" in result:
        st.subheader("Raw Results")
        st.write({"columns": result["columns"], "rows": result["rows"]})

    st.subheader("Answer")
    st.success(result["answer"])