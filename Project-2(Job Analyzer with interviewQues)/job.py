pip install langchain-core langchain_groq langchain_community
import os

from langchain_groq import ChatGroq
llm= ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)
response=llm.invoke("Who is Ganesha?")
print(response.content)

from langchain_community.document_loaders import WebBaseLoader
loader= WebBaseLoader("https://www.shine.com/jobs/ml-engineer/hdiplatform/18882015?utm_campaign=google_jobs_apply&utm_source=google_jobs_apply&utm_medium=organic")
page_data= loader.load().pop().page_content
print(page_data)

from langchain_core.prompts import PromptTemplate
prompt_extract= PromptTemplate.from_template(""" ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the
        following keys: `role`, `experience`, `skills` and `description`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):"""

)
chain_extract= prompt_extract | llm
res= chain_extract.invoke(input ={'page_data': page_data})
print(res.content)

