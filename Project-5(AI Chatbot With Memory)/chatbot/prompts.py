from langchain_core.prompts import PromptTemplate
CHAT_PROMPT= PromptTemplate(
    input_variables= ["history", "input"],
    template= """You are a helpful assistant. You have access to the following .

    conversation history:
    {history}

    Human:{input}
    AI:  """
    )