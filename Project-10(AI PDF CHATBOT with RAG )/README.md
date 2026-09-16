# 📄 Project 10: AI PDF Chatbot with RAG (25 Q&A Hinglish Guide)

Welcome to **Project 10: AI PDF Chatbot with RAG**! 🚀
Is project me hum seekhenge ki **Retrieval-Augmented Generation (RAG)** architecture kya hota hai aur kaise hum kisi bhi PDF ya document ke base par ek intelligent AI assistant create kar sakte hain jo bina hallucination ke factual jawab deta hai.

---

## 📂 RAG Core Architecture

```
[Raw PDF Document]
        │
        ▼
1. Document Loader (PyPDFLoader / docs2txt)
        │
        ▼
2. Text Splitter (RecursiveCharacterTextSplitter: chunk_size & overlap)
        │
        ▼
3. Embedding Model (SentenceTransformers / Google GenAI Embeddings)
        │
        ▼
4. Vector Store (FAISS / Chroma DB: Indexing & Storage)
        │
        ▼
────────────────────────── RUNTIME ──────────────────────────
        │
User Query ("PDF ke page 5 par revenue target kya likha hai?")
        │
        ▼
5. Retriever (Cosine Similarity Top-k Chunks Fetch)
        │
        ▼
6. Augmented Prompt (Context + User Query)
        │
        ▼
7. LLM (Google Gemini / ChatOpenAI)
        │
        ▼
Final Factual Answer with Sources!
```

---

## 📚 25 Questions & Answers (Hinglish Guide)

### Q1: RAG (Retrieval-Augmented Generation) ka basic concept kya hai?
**Answer:**
RAG do cheezon ka combination hai:
1. **Retrieval (Dhoondna):** External knowledge base (jaise aapki personal PDF) me se relevant information dhoondna.
2. **Generation (Likhna):** LLM (jaise Gemini ya GPT) dwara us mili hui information ko padhkar user ke sawal ka simple language me jawab likhna.
Yeh LLM ko *"Open Book Exam"* dene jaisa hai. Model ko sab kuch ratne ki zaroorat nahi hoti, wo kitaab (retrieved context) samne khol kar answer deta hai.

---

### Q2: RAG ki zaroorat kyun padi? Kyun na direct LLM se sawal puch lein?
**Answer:**
Agar aap ChatGPT ya Gemini se puchein: *"Meri company ki latest quarterly policy kya hai?"*, toh wo nahi bata payega kyunki:
1. **Private Data:** Company ki PDF public internet par nahi hai.
2. **Knowledge Cutoff:** Model ka training data purana hota hai.
3. **Hallucination:** Data na hone par model man-ghadant kahani (fake answer) bana deta hai.
RAG in teeno problems ko 100% solve kar deta hai.

---

### Q3: Is project me kaun-kaun se components aur libraries use hui hain?
**Answer:**
- **LangChain (`langchain`, `langchain-core`, `langchain-community`)**: Orchestration framework.
- **`langchain_google_genai`**: Google Gemini API ke sath integration.
- **`pypdf` / `docs2txt`**: PDF se text extract karne ke liye.
- **`langchain_chroma` / `faiss-cpu`**: Vector databases.
- **`sentence_transformers`**: Open-source local text embedding models.
- **LangSmith**: Monitoring aur tracing tool.

---

### Q4: Fine-Tuning vs RAG me kya difference hai? Humein kab kya use karna chahiye?
**Answer:**

| Parameter | RAG | Fine-Tuning |
|-----------|-----|-------------|
| **Data Update** | Instant (Bas nayi PDF folder me daalo) | Expensive (Har baar retrain karna padega) |
| **Cost** | Bohot cheap / Free | GPUs aur high compute cost |
| **Source Citation** | Haan (Page number quote kar sakta hai) | Nahi (Direct weights me blend ho jata hai) |
| **Best For** | Factual Q&A on private documents | Tone, style, ya naye syntax sikhane ke liye |

Document Q&A ke liye **RAG hamesha better option hota hai**.

---

### Q5: Document Loader kya hota hai aur iska kya kaam hai?
**Answer:**
PDF, Word (.docx), ya text files binary format me hoti hain. Document Loader (e.g. `PyPDFLoader`) file ko read karke raw text ko LangChain ke `Document` object me convert karta hai jisme do cheezein hoti hain:
1. `page_content`: Us page ka actual text.
2. `metadata`: Source file name, page number, creation date, etc.

---

### Q6: RecursiveCharacterTextSplitter kyun use kiya jata hai?
**Answer:**
Badi files ko chote chunks me todna padta hai. `RecursiveCharacterTextSplitter` sabse smart splitter hai kyunki yeh text ko natural boundaries par split karta hai:
1. Pehle double newline (`\n\n`) par paragraphs alag karta hai.
2. Fir single newline (`\n`) par lines alag karta hai.
3. Fir spaces (` `) par words alag karta hai.
Isse kabhi koi sentence beech me se adha nahi tutta!

---

### Q7: `chunk_size` aur `chunk_overlap` ka perfect balance kya hai?
**Answer:**
- `chunk_size`: Ek chunk me maximum kitne characters/tokens honge (e.g. 1000).
- `chunk_overlap`: Pichle chunk ke kitne characters agle chunk me repeat honge (e.g. 200).
- **Rule of Thumb:** Overlap hamesha chunk size ka 10% se 20% hona chahiye. Agar chunk size 1000 hai, toh 150-200 overlap best rehta hai.

---

### Q8: Text Embeddings kya hoti hain aur yeh kaise calculate hoti hain?
**Answer:**
Embedding ek mathematical function hai jo text ko floating-point numbers ki list (vector) me convert karta hai (e.g. 768-dimensional vector).
Agar do sentences ka meaning similar hai (e.g. *"Ronaldo plays football"* aur *"CR7 is a soccer player"*), toh unke vectors ke beech ka distance bohot kam hoga.

---

### Q9: `sentence_transformers` open-source embeddings vs Google/OpenAI embeddings me kya antar hai?
**Answer:**
- **Sentence Transformers (`all-MiniLM-L6-v2`)**: Aapke apne computer ke CPU/GPU par locally run hota hai. 100% free hai, privacy safe rehti hai, koi API call nahi hoti.
- **Google / OpenAI Embeddings**: Cloud API par run hoti hain. Quality thodi higher hoti hai par API key aur internet connection mandatory hota hai.

---

### Q10: Vector Store (FAISS ya Chroma) kya hota hai?
**Answer:**
Normal relational databases (MySQL, Postgres) numbers ke beech semantic similarity search nahi kar sakte. Vector Database high-dimensional vectors ko index karta hai aur **Approximate Nearest Neighbor (ANN)** search run karta hai taaki lakho documents me se seconds me top-3 ya top-5 matching passages mil sakein.

---

### Q11: Cosine Similarity vs Euclidean Distance (L2) me kya farak hai?
**Answer:**
- **Cosine Similarity:** Do vectors ke beech ka angle dekhta hai. Yeh text length par depend nahi karta (chahe ek short sentence ho aur dusra lamba paragraph, agar topic same hai toh angle zero hoga). RAG me sabse zyada yahi use hota hai.
- **Euclidean Distance (L2):** Do points ke beech ki absolute physical doori naapta hai.

---

### Q12: LangChain Expression Language (LCEL) kya hoti hai?
**Answer:**
LCEL LangChain ka modern declarative way hai chains compose karne ka. Isme pipe operator (`|`) use hota hai:
```python
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```
Yeh code ko clean, streaming-friendly, aur parallel execution ke kaabil banata hai.

---

### Q13: "Retriever" kya hota hai aur `k` parameter ka kya matlab hai?
**Answer:**
Retriever vector database ka wrapper hota hai. Jab aap bolte hain:
```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```
Iska matlab hai user ke sawal se sabse zyada milte-julte top-3 relevant chunks database se nikaal kar LLM ko bhejo.

---

### Q14: RAG me Context Injection Prompt kaisa banaya jata hai?
**Answer:**
```text
System: You are an expert assistant for question-answering tasks.
Use ONLY the following pieces of retrieved context to answer the question.
If you don't know the answer or it's not in the context, say "I don't know".
Do NOT make up facts.

Context:
{context}

Question: {question}
Answer:
```
Yeh strict instruction model ko hallucination create karne se rokti hai.

---

### Q15: LangSmith Tracing (`LANGCHAIN_TRACING_V2="true"`) kya karta hai?
**Answer:**
RAG pipeline ke andar kya ho raha hai, yeh terminal par dekhna mushkil hota hai. LangSmith ek observability platform hai jo visual dashboard par dikhata hai:
- User ka exact question kya tha.
- Retriever ne kaun-kaun se document chunks nikale.
- Prompt me kitne tokens gaye aur LLM ko answer generate karne me kitne milliseconds lage.

---

### Q16: "Stuffing" vs "Map-Reduce" RAG chains me kya fark hai?
**Answer:**
- **Stuff Documents:** Saare top chunks ko ek hi prompt me "stuff" (daal) kar ek baar me LLM ko bhej diya jata hai. Fast aur sasta hota hai (90% standard RAG me yahi use hota hai).
- **Map-Reduce:** Agar documents bohot zyada hain, toh har chunk ka alag answer banakar aakhiri me combine kiya jata hai.

---

### Q17: RAG me Hallucination ko zero kaise karein?
**Answer:**
1. Temperature ko `0.0` set karein.
2. Prompt me strictly likhein: *"Rely only on provided context"*.
3. Similarity score threshold lagayein — agar match score 0.7 se kam ho toh answer dene se mana kar dein.

---

### Q18: Source Attribution (Citations) kaise di jaati hain?
**Answer:**
Retrieved `Document` object ke andar `metadata` mojud hota hai:
```python
for doc in retrieved_docs:
    print(f"Source: {doc.metadata['source']}, Page: {doc.metadata['page']}")
```
LLM response ke niche user ko exact PDF page number display kiya ja sakta hai taaki user verify kar sake.

---

### Q19: Google Gemini (`ChatGoogleGenerativeAI`) ko RAG ke sath kaise initialize karte hain?
**Answer:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.environ["GOOGLE_GENAI_API_KEY"]
)
```

---

### Q20: Agar PDF scanned image ho (text copy nahi hota), tab RAG kaise kaam karega?
**Answer:**
Normal `PyPDFLoader` blank text return karega. Aisi PDFs ke liye **OCR (Optical Character Recognition)** ya Multimodal Vision LLMs (jaise `Qwen-2.5 VL` ya `Gemini Vision`) use karke pehle image se text extract karna padta hai, fir RAG me bhejna hota hai.

---

### Q21: FAISS Index ko disk par save aur load kaise karte hain?
**Answer:**
- **Save karna:**
  ```python
  vectorstore.save_local("faiss_index")
  ```
- **Load karna (Har baar embeddings calculate nahi karni padti):**
  ```python
  new_vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
  ```

---

### Q22: `OutputParser` ka kya role hota hai?
**Answer:**
LLM ka raw output ek complex `AIMessage` object hota hai jisme metadata aur token counts hote hain. `StrOutputParser()` usme se sirf clean plain text string extract karke aage pass karta hai.

---

### Q23: Kya RAG multiple PDFs ko ek sath handle kar sakta hai?
**Answer:**
Haan! LangChain ka `DirectoryLoader` poore folder ki 50 PDFs ko ek sath load karke single FAISS index me save kar sakta hai. Jab user sawal puchega, toh retriever sabhi files me se best context nikaal layega.

---

### Q24: RAG application evaluate kaise ki jaati hai (RAG Triad)?
**Answer:**
3 metrics par RAG judge hota hai:
1. **Context Relevance:** Kya retriever ne sahi context dhoonda?
2. **Groundedness:** Kya answer sach me context ke andar mojud data se diya gaya hai?
3. **Answer Relevance:** Kya answer user ke pucho gaye sawal ka direct solution hai?

---

### Q25: Is Project ko local machine par run karne ka workflow:
**Answer:**
```bash
# 1. Project folder me switch karein
cd "j:/3Generative Ai/Project-10(AI PDF CHATBOT with RAG )"

# 2. Virtual environment activate karein
.\myenv\Scripts\activate

# 3. Required packages install karein
pip install -r requirements.txt

# 4. Jupyter Notebook open karein
jupyter notebook langchain_rag_chatbot.ipynb
```
Notebook ke cells ko sequentially run karke aap live RAG pipeline execute kar sakte hain! 🎉
