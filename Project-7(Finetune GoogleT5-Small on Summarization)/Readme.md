# 🎯 Project 7: Fine-Tuning Google T5-Small on Dialogue Summarization (25 Q&A Hinglish Guide)

Welcome to **Project 7: Fine-Tuning Google T5-Small on Dialogue Summarization**! 🚀
Is project me hum seekhenge ki kaise ek pre-trained Seq2Seq (Sequence-to-Sequence) model **Google T5-Small** ko chat/dialogue conversations ki natural summary banane ke liye **Hugging Face Transformers** aur **PyTorch** ke zariye fine-tune kiya jata hai.

---

## 📂 Fine-Tuning Pipeline Architecture

```
[SAMSum Dialogue Dataset] (Human-to-Human Casual Chat)
            │
            ▼
[T5 Tokenizer: AutoTokenizer.from_pretrained("t5-small")]
  Prefix: "summarize: " added to input text
            │
            ▼
[Data Preprocessing & Tokenization]
  max_input_length=512 | max_target_length=128
            │
            ▼
[DataCollatorForSeq2Seq] ──> Dynamic padding & label masking (-100 for pad tokens)
            │
            ▼
[Base Model: AutoModelForSeq2SeqLM ("t5-small" - 60M parameters)]
            │
            ▼
[Seq2SeqTrainer + Seq2SeqTrainingArguments]
  fp16 / bf16 | Learning Rate=5e-5 | AdamW | Evaluation Strategy="epoch"
            │
            ▼
[Evaluation Metric: ROUGE Score (ROUGE-1, ROUGE-2, ROUGE-L)]
            │
            ▼
[Fine-Tuned Model Saved to Disk] ──> High-quality dialogue summarization inference!
```

---

## 📚 25 Questions & Answers (Hinglish Guide)

### Q1: Is Project ka main objective kya hai?
**Answer:**
Standard base models (jaise Google T5-Small) formal news articles toh summarize kar lete hain, lekin doston ki casual chatting, WhatsApp-style slang, aur informal dialogues ko acche se summarize nahi kar pate. Is project me hum T5 model ko specifically **conversational dialogues** ko accurately summarize karne ke liye train (fine-tune) karte hain.

---

### Q2: Google T5 (Text-to-Text Transfer Transformer) kya hota hai?
**Answer:**
Google dwara banaya gaya ek revolutionary NLP model jisme **har NLP problem ko ek text-to-text format** me cast kiya jata hai:
- *Translation:* `"translate English to German: How are you?"` $\rightarrow$ `"Wie geht es dir?"`
- *Classification:* `"sst2 sentence: I loved the film"` $\rightarrow$ `"positive"`
- *Summarization:* `"summarize: [Long passage]"` $\rightarrow$ `"[Short summary]"`
Har input text hota hai, aur har output bhi text hota hai!

---

### Q3: T5-Small model kitna bada hai aur isme kitne parameters hain?
**Answer:**
`t5-small` me lagbhag **60 Million (60M) parameters** hote hain. Yeh lightweight hai, Google Colab ke free GPU (T4) par easily aur tezi se fine-tune ho jata hai bina out-of-memory (OOM) error ke.

---

### Q4: SAMSum Dataset kya hai aur isme kaisa data hota hai?
**Answer:**
SAMSum ek specialized NLP dataset hai jisme real-life jaise chat conversations hote hain:
- **Dialogue:**
  ```text
  John: Are you coming to the football match tonight?
  Sarah: I have to finish my assignment first, might be 30 mins late.
  John: Cool, I will save a seat for you near the front row.
  ```
- **Summary:**
  ```text
  Sarah will be late to the football match because of her assignment. John will save a seat for her.
  ```

---

### Q5: T5 me input prompt ke aage `"summarize: "` prefix lagana kyun zaroori hai?
**Answer:**
T5 ek multi-task model hai. Jab tak aap use batayenge nahi ki use kya task karna hai, wo confuse ho sakta hai. `"summarize: "` prefix model ko signal deta hai ki use text ko summarize karna hai, translate nahi!
```python
prefix = "summarize: "
inputs = [prefix + doc for doc in examples["dialogue"]]
```

---

### Q6: `DataCollatorForSeq2Seq` kya hota hai aur dynamic padding kyun zaroori hai?
**Answer:**
- Agar batch me sabhi sentences 512 length ke fix kar diye jayein, toh chote sentences par faltu ke `<pad>` tokens process honge jisse GPU compute waste hoga.
- `DataCollatorForSeq2Seq` har batch ke sabse lambe sentence ke hisab se dynamically pad karta hai.
- Yeh target labels me padding tokens ko `-100` se replace karta hai taaki PyTorch loss calculation ke waqt unhe ignore kar sake.

---

### Q7: PyTorch me Cross-Entropy Loss padding tokens par `-100` ko kyun ignore karta hai?
**Answer:**
PyTorch `CrossEntropyLoss(ignore_index=-100)` by default `-100` index wale labels ko loss calculation me count nahi karta. Padding tokens model ki galti nahi hote, isliye unpar model ko punish nahi karna chahiye.

---

### Q8: ROUGE Metric (ROUGE-1, ROUGE-2, ROUGE-L) ka summarization me kya role hai?
**Answer:**
Summaries ko accuracy percentage se check nahi kiya ja sakta kyunki do log ek hi chat ko alag shabdon me summarize kar sakte hain.
- **ROUGE-1:** Single words (unigrams) ka ground truth se overlap.
- **ROUGE-2:** 2-word phrases (bigrams) ka overlap (fluency check karta hai).
- **ROUGE-L:** Longest Common Subsequence (sentence structure ka match).

---

### Q9: `evaluate.load("rouge")` library kaise score nikaalti hai?
**Answer:**
```python
rouge = evaluate.load("rouge")
result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
```
`use_stemmer=True` lagane se root words match hote hain (e.g. `"running"` aur `"runs"` ko same root `"run"` maana jata hai).

---

### Q10: Learning Rate `5e-5` ($0.00005$) kyun choose kiya gaya?
**Answer:**
Fine-tuning me learning rate hamesha bohot chota hona chahiye. Agar hum bada learning rate (e.g. `0.01`) denge, toh T5 ke pre-trained weights destroy ho jayenge (**Catastrophic Forgetting**). Chota learning rate model ke pre-trained knowledge ko preserve rakhte hue use naye task me adapt karta hai.

---

### Q11: Mixed Precision Training (`fp16=True`) ka kya fayda hai?
**Answer:**
Traditional training standard 32-bit floating point (`float32`) par hoti hai. `fp16=True` model computations ko 16-bit half precision me convert karta hai:
- GPU memory (VRAM) 50% kam lagti hai.
- Training speed lagbhag 2x faster ho jaati hai bina accuracy compromise kiye.

---

### Q12: `Seq2SeqTrainingArguments` ke key hyper-parameters kya hain?
**Answer:**
- `per_device_train_batch_size=8`: Ek step me kitne samples GPU me jayenge.
- `num_train_epochs=3`: Poore dataset ko model kitni baar dekhega.
- `weight_decay=0.01`: Overfitting rokne ke liye regularization.
- `predict_with_generate=True`: Validation step par greedy/beam search se actual text generate karke ROUGE score calculate karta hai.

---

### Q13: `predict_with_generate=True` kyun mandatory hai?
**Answer:**
Agar yeh parameter nahi lagayenge, toh validation ke time model sirf raw loss calculate karega, actual text string generate nahi karega. Actual text generate na hone par ROUGE score calculate nahi ho payega.

---

### Q14: Encoder-Decoder Architecture me T5 Encoder aur Decoder ka kya kaam hai?
**Answer:**
- **Encoder:** Poore dialogue ko ek sath padhta hai (Bidirectional Attention) aur conversation ka deep context representation banata hai.
- **Decoder:** Summary ko ek-ek word karke generate karta hai (Causal Masked Attention) aur Encoder ke context ko cross-attention ke zariye refer karta rehta hai.

---

### Q15: SentencePiece Tokenizer kya hota hai?
**Answer:**
T5 SentencePiece tokenizer use karta hai. Yeh text ko language-agnostic subwords me break karta hai aur words ke aage underscore (`_`) lagata hai spaces preserve karne ke liye:
`"Hello world"` $\rightarrow$ `["_Hello", "_world"]`.

---

### Q16: Zero-Shot vs Fine-Tuned T5-Small Performance me kya difference dikhta hai?
**Answer:**
- **Zero-shot T5 (Bina training ke):** Dialogue me se bas pehli 2 lines utha kar bol deta hai ya ajeeb si grammatical summary deta hai.
- **Fine-Tuned T5 (Training ke baad):** Dialogue ke core emotion, speaker ke decisions, aur plans ko samajhkar crisp 1-2 line summary generate karta hai.

---

### Q17: Model Overfitting ko detect kaise karein?
**Answer:**
Training logs me `train_loss` aur `val_loss` ko monitor karein:
- Agar `train_loss` lagatar ghir raha hai aur `val_loss` badhne lage, toh model overfit ho raha hai.
- Isko rokne ke liye Early Stopping ya Dropout badhaya jata hai.

---

### Q18: Fine-Tuned Model ko disk par save kaise karte hain?
**Answer:**
```python
trainer.save_model("./saved_t5_samsum_model")
tokenizer.save_pretrained("./saved_t5_samsum_model")
```
Yeh folder me `pytorch_model.bin` (ya `model.safetensors`), `config.json`, aur `tokenizer.json` save kar deta hai.

---

### Q19: Saved fine-tuned model ko production inference me kaise load karein?
**Answer:**
Hugging Face `pipeline` ke zariye:
```python
from transformers import pipeline

summarizer = pipeline("summarization", model="./saved_t5_samsum_model")
summary = summarizer("summarize: John: Hey are you coming? Sarah: Yes on my way!")
print(summary[0]["summary_text"])
```

---

### Q20: Beam Search vs Greedy Search summarization me kya hota hai?
**Answer:**
- **Greedy Search (`num_beams=1`):** Fast hota hai par boring/repetitive text de sakta hai.
- **Beam Search (`num_beams=4`):** Model har step par top-4 best sequence branches ko explore karta hai. Summaries grammatically zyada coherent banti hain.

---

### Q21: GPU Memory OOM (Out Of Memory) crash se kaise bachein?
**Answer:**
1. `per_device_train_batch_size` ko 8 se kam karke 4 ya 2 kar dein.
2. `gradient_accumulation_steps=2` ya `4` lagayein (chote batches ko accumulate karke virtual bada batch bana deta hai).
3. `max_input_length` ko 512 se reduce karke 384 kar dein.

---

### Q22: Hugging Face Datasets library ka memory efficiency me kya role hai?
**Answer:**
`load_dataset("samsum")` poore dataset ko RAM me load nahi karti, balki Apache Arrow format me memory-mapped disk caching use karti hai. Isse 100 GB ka dataset bhi 8 GB RAM wale system par smoothly process ho jata hai.

---

### Q23: Accelerate library ka kya role hai?
**Answer:**
Hugging Face `accelerate` background me automatically detect karti hai ki aap CPU, single GPU, Multi-GPU, ya TPU par hain, aur bina code badle distributed training optimize kar deti hai.

---

### Q24: Fine-tuned model ko Hugging Face Hub par public share kaise karein?
**Answer:**
```python
trainer.push_to_hub("your-username/t5-small-samsum-dialogue-summary")
```
Model public ho jayega aur duniya me koi bhi use `pipeline("summarization", model="your-username/...")` se load kar sakega.

---

### Q25: Is Project ko Google Colab ya Local Machine par run karne ka workflow:
**Answer:**
```bash
# 1. Required libraries install karein
pip install transformers datasets accelerate sentencepiece evaluate rouge_score torch

# 2. Training script run karein ya Google Colab notebook me execute karein
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```
Colab me GPU runtime (T4 GPU) select karein aur full training code execute karein. 15-20 minutes me aapka fine-tuned model ready ho jayega! 🎉