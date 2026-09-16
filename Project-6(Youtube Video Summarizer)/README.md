# 🎬 Project 6: YouTube Video Summarizer (25 Q&A Hinglish Guide)

Welcome to **Project 6: YouTube Video Summarizer**! 🚀
Yeh ek production-ready, full-stack Generative AI application hai jo kisi bhi YouTube video ka URL lekar uska transcript extract karti hai, concurrent Map-Reduce summarization karti hai, timestamped chapters banati hai, API token cost track karti hai, SQLite cache maintain karti hai, RAG Q&A allow karti hai, aur PDF/Markdown export facilitate karti hai.

---

## 📂 System Architecture Flow

```
[YouTube Video URL]
        │
        ▼
[src/transcript_fetcher.py] ──> Extracts video_id & fetches subtitles/transcript
        │
        ▼
[src/cache.py] ──> Checks SQLite DB (`summarizer_cache.sqlite3`)
        │
    ┌───┴───┐
[Cached]  [Not Cached]
    │       │
    │       ▼
    │   [src/chunker.py] ──> Splits transcript into token-bounded chunks
    │       │
    │       ▼
    │   [src/summarizer.py] ──> Concurrent Map Phase (ThreadPoolExecutor)
    │       │
    │       ▼
    │   [Reduce Phase] ──> Final comprehensive summary
    │       │
    │       ▼
    │   [src/chapters.py] ──> Generates timestamped video chapters
    │       │
    │       ▼
    │   [src/cost_tracker.py] ──> Calculates prompt & completion token dollars
    │       │
    │       ▼
    └──> [src/qa_engine.py] ──> Interactive follow-up Q&A on video content
            │
            ▼
        [src/export.py] ──> Export to Markdown / PDF
```

---

## 📚 25 Questions & Answers (Hinglish Guide)

### Q1: Yeh YouTube Summarizer project aakhir kya problem solve karta hai?
**Answer:**
Aaj kal YouTube par 1-2 ghante ke lambe podcasts, lectures aur tutorials hote hain. Kisi ke paas poora video dekhne ka time nahi hota. Yeh app kisi bhi video URL ko paste karne par 15-30 seconds ke andar poore video ka summary, key insights, timestamped chapters aur follow-up Q&A provide kar deta hai.

---

### Q2: Project me kaun-kaun si major modules aur files shamil hain?
**Answer:**
- `app.py`: Interactive Streamlit Web Dashboard.
- `cli.py`: Terminal/Command Line Interface.
- `config.py`: Centralized configuration aur hyperparameters.
- `src/transcript_fetcher.py`: YouTube se raw subtitles/transcripts download karta hai.
- `src/chunker.py`: Lambe transcripts ko token-safe chunks me divide karta hai.
- `src/summarizer.py`: Map-Reduce parallel summarization engine.
- `src/chapters.py`: Timestamps ke sath logical chapters create karta hai.
- `src/cache.py`: SQLite caching engine.
- `src/cost_tracker.py`: Real-time API token usage aur pricing calculator.
- `src/qa_engine.py`: Video ke content par follow-up chat engine (RAG).
- `src/export.py`: Summary ko Markdown aur PDF me convert karta hai.

---

### Q3: YouTube video se transcript bina video download kiye kaise fetch hota hai?
**Answer:**
`youtube-transcript-api` library ke zariye. Yeh library YouTube ke internal subtitle API endpoints ko request bhejti hai aur video ki XML/JSON captions fetch kar leti hai bina heavy MP4 video file download kiye. Isse bandwidth aur time 99% save hota hai.

---

### Q4: Video ID extraction regex kaise kaam karta hai? (`extract_video_id`)
**Answer:**
YouTube URLs alag-alag formats me aate hain:
- Standard: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short: `https://youtu.be/dQw4w9WgXcQ`
- Embed: `https://www.youtube.com/embed/dQw4w9WgXcQ`
Regex in sabhi patterns se exact 11-character ka unique video ID nikaalta hai.

---

### Q5: Agar kisi YouTube video me captions/subtitles disable hon, tab kya hota hai?
**Answer:**
`src/transcript_fetcher.py` me custom `TranscriptError` exception raise hota hai. UI crash nahi hoti, balki clean error message show hota hai: *"No transcripts found for this video. Either subtitles are disabled or video is private."*

---

### Q6: Lambe transcripts ke liye Map-Reduce summarization kyun zaroori hai?
**Answer:**
Agar video 3 ghante ka hai, toh transcript 40,000+ tokens ka ho sakta hai. Agar hum poora transcript ek baar me LLM ko bhejenge:
1. Rate limit (TPM - Tokens Per Minute) exceed ho jayega.
2. Model ka response slow ho jayega.
3. Attention dilute ho jayegi aur beech ki details miss ho jayengi ("Lost in the Middle" problem).

---

### Q7: Map Phase aur Reduce Phase step-by-step kaise kaam karte hain?
**Answer:**
- **Map Phase:** Transcript ko 4-5 chunks me todkar parallel threads (`ThreadPoolExecutor`) se har chunk ki mini-summary banayi jaati hai.
- **Reduce Phase:** Sabhi mini-summaries ko ek sath combine karke final prompt banaya jata hai jo ek clean, cohesive executive summary generate karta hai.

---

### Q8: `ThreadPoolExecutor` se concurrency kaise implement ki gayi hai?
**Answer:**
Agar 5 chunks hain aur sequential bhejenge toh 5 × 4 sec = 20 seconds lagenge. `ThreadPoolExecutor(max_workers=5)` un sabhi 5 chunks ko simultaneously OpenAI server par bhejta hai, jisse saari summaries sirf 4-5 seconds me complete ho jaati hain!

---

### Q9: Timestamped Chapters (`src/chapters.py`) kaise generate hote hain?
**Answer:**
Har transcript segment ke sath uska `start_time` (seconds me) attach hota hai. Model chunked summary ke shuru hone ka time convert karta hai `HH:MM:SS` format me (e.g. `[05:23] - Machine Learning Architecture`), jisse user direct us time par video skip kar sake.

---

### Q10: SQLite Caching (`src/cache.py`) ka kya fayda hai?
**Answer:**
Database `summarizer_cache.sqlite3` me video ID ko primary key banakar summarized output save kiya jata hai.
- Jab koi user dubara wahi URL paste karta hai:
  - Cache hit hota hai!
  - 0 API calls lagti hain ($0.00 cost).
  - Response 0.1 second me render ho jata hai.

---

### Q11: Cost Tracking (`src/cost_tracker.py`) kaise kaam karta hai?
**Answer:**
OpenAI API response me `usage` object return karti hai:
- `prompt_tokens`
- `completion_tokens`
Hamara cost tracker exact model (e.g. GPT-4o-mini: $0.15 / 1M input tokens, $0.60 / 1M output tokens) ke hisab se exact dollars calculate karke UI me display karta hai: *"Total Cost: $0.0024"*.

---

### Q12: Follow-up RAG Q&A Engine (`src/qa_engine.py`) kya karta hai?
**Answer:**
Summary padhne ke baad agar user video ke kisi specific topic par gehra sawal puchna chahe:
*"Is video me author ne Rust language ke baare me kya bola?"*
QA engine transcript ko index karke exact line retrieve karta hai aur accurate context-grounded answer deta hai.

---

### Q13: Export Functionality (`src/export.py`) me kaun se formats supported hain?
**Answer:**
1. **Markdown (`.md`)**: Notes apps (Obsidian, Notion) me import karne ke liye formatted text file.
2. **PDF (`.pdf`)**: Printable document report jo `ReportLab` ya `fpdf2` ke zariye byte-stream me generate hoti hai.

---

### Q14: Streamlit UI me kaun-kaun se interactive controls diye gaye hain?
**Answer:**
- Model selector: `gpt-4o-mini`, `gpt-4o`, `gpt-4.1-mini`.
- Slider: `Max tokens per chunk` (500 - 4000).
- Slider: `Concurrent chunk requests` (1 - 10 workers).
- Custom OpenAI API Key input box (agar user apni key use karna chahe).

---

### Q15: `mock_llm.py` ka kya role hai?
**Answer:**
Testing aur offline development ke liye! Agar aapke paas active internet ya OpenAI API balance nahi hai, toh `mock_llm.py` bina real API call kiye realistic fake summaries generate karta hai taaki frontend UI aur code logic test kiya ja sake bina paise kharch kiye.

---

### Q16: Unit Tests (`tests/test_chunker.py`, `tests/test_cost_tracker.py`) kaise verify karte hain?
**Answer:**
- `test_chunker.py`: Check karta hai ki token count boundary cross na ho aur time continuity break na ho.
- `test_cost_tracker.py`: Mathematical token pricing calculations ko verify karta hai.

---

### Q17: Terminal se CLI mode me summarizer kaise run karein?
**Answer:**
```bash
python cli.py "https://www.youtube.com/watch?v=VIDEO_ID" --model gpt-4o-mini --export markdown
```
Yeh bina browser khole terminal par instant summary print kar deta hai.

---

### Q18: Pytest commands se saare tests kaise run karein?
**Answer:**
```bash
pytest tests/ -v
```

---

### Q19: Docker aur Docker Compose support kaise structured hai?
**Answer:**
Project me `Dockerfile` aur `docker-compose.yml` mojud hain. Sirf ek command se:
```bash
docker-compose up --build
```
Poora summarizer containerize hokar port 8501 par live ho jata hai bina host machine par Python packages install kiye.

---

### Q20: `video_meta.py` video title kaise extract karta hai?
**Answer:**
YouTube ke oEmbed public endpoint (`https://www.youtube.com/oembed?url=...&format=json`) ko call karke bina official YouTube Data v3 API Key ke bhi video ka real title aur author name instantly mil jata hai.

---

### Q21: Streamlit caching (`@st.cache_data`) aur SQLite Cache me kya difference hai?
**Answer:**
- `st.cache_data`: In-memory RAM cache hai. Jab server restart hota hai, RAM khali ho jaati hai.
- `SQLite Cache`: Persistent disk cache hai. Server band hone ke mahino baad bhi data surakshit rehta hai.

---

### Q22: Rate Limits aur Exponential Backoff kaise handle hote hain?
**Answer:**
OpenAI API agar `RateLimitError` (HTTP 429) de, toh code `tenacity` library ya custom retry loop ke zariye 2, 4, 8 seconds ruk kar automatically retry karta hai.

---

### Q23: Is project me `.env` configuration:
**Answer:**
```env
OPENAI_API_KEY=sk-your-key-here
MAX_CONCURRENT_REQUESTS=5
CACHE_DB_PATH=summarizer_cache.sqlite3
```

---

### Q24: Cost reduction ke liye best model recommendation kya hai?
**Answer:**
`gpt-4o-mini` use karein! Yeh GPT-3.5 se zyada smart hai aur GPT-4 ke mukable 90%+ sasta hai. Ek 30-minute ke video ko summarize karne ka kharch $0.003 (lagbhag 25 paise) se bhi kam aata hai.

---

### Q25: Is Project ko local computer par run karne ka step-by-step guide:
**Answer:**
```bash
# 1. Directory me jayein
cd "j:/3Generative Ai/Project-6(Youtube Video Summarizer)"

# 2. Virtual environment activate karein
.\venv\Scripts\activate

# 3. Packages install karein
pip install -r requirements.txt

# 4. Streamlit UI launch karein
streamlit run app.py
```
Browser open karein, YouTube link paste karein, aur summary enjoy karein! 🎉
