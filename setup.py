from setuptools import setup, find_packages

setup(
    name="mcqgen",
    version="0.1",
    author="Aditya Singh",
    author_email="adityasingh@example.com",
    packages=find_packages(),
    install_requires=[
        "langchain-openai",
        "langchain-core",
        "langchain-community",
        "streamlit",
        "python-dotenv",
        "PyPDF2",
        "pandas"
    ],
)