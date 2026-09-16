try:
    from langchain_community.memory import ConversationBufferMemory
except ImportError:
    try:
        from langchain.memory import ConversationBufferMemory
    except ImportError:
        from langchain_classic.memory import ConversationBufferMemory

def get_memory():
    return ConversationBufferMemory(
        memory_key="history",
        input_key="input"
    )