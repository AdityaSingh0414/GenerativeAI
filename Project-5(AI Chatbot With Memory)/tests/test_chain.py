import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatbot.chain import build_chain

chain = build_chain(provider="groq")  # or "openai"

print(chain.predict(input="Hi, my name is Aditya."))
print(chain.predict(input="What's my name?"))   # should correctly recall "Aditya"
print(chain.predict(input="I like building AI projects."))
print(chain.predict(input="What do I like doing, and what's my name?"))