# 🏗️ Project 9: Build LLM From Scratch (25 Q&A Hinglish Guide)

Welcome to **Project 9: Build LLM From Scratch**! 🚀
Is project me hum bina kisi pre-built heavy library (jaise HuggingFace ya LangChain) ke, bilkul **zero se PyTorch me ek GPT-style Decoder-Only Large Language Model** design aur implement karna seekhte hain.

---

## 🏛️ GPT Model Architecture Roadmap

```
Raw Text ("Generative AI is amazing")
             │
             ▼
1. Tokenization (Byte-Pair Encoding - BPE Tokenizer)
   Text ──> Token IDs: [15496, 7268, 318, 4998]
             │
             ▼
2. Embedding Layer
   Token Embeddings + Positional Embeddings
             │
             ▼
3. Transformer Blocks (Stacked × N Layers)
   ┌─────────────────────────────────────────────────┐
   │  ┌──> Layer Normalization 1                     │
   │  │    Multi-Head Causal Self-Attention (Q, K, V)│
   │  └──> Residual Connection (Skip Highway) ───────┼──(+)
   │                                                 │
   │  ┌──> Layer Normalization 2                     │
   │  │    Feed-Forward Network (Linear + GELU)      │
   │  └──> Residual Connection (Skip Highway) ───────┼──(+)
   └─────────────────────────────────────────────────┘
             │
             ▼
4. Final LayerNorm & Linear Output Head (Logits)
             │
             ▼
5. Softmax & Cross-Entropy Loss / Next-Token Sampling
   Predicted Next Word ("!")
```

---

## 📚 25 Questions & Answers (Hinglish Guide)

### Q1: "Build LLM From Scratch" ka matlab kya hai?
**Answer:**
Aam taur par hum OpenAI ya Google ki bani-banai APIs use karte hain. Lekin is project me hum kisi API ka use nahi karte. Hum **PyTorch ke basic tensors aur math functions** ka use karke khud ka neural network architecture, attention layer, tokenizer, aur training loop code karte hain jisse hume samajh aaye ki LLM ke andar ka har ek purza (component) kaise kaam karta hai.

---

### Q2: GPT Architecture kis type ka Transformer hota hai?
**Answer:**
Transformers ke teen variants hote hain:
1. **Encoder-Only (e.g. BERT):** Text understanding aur classification ke liye.
2. **Encoder-Decoder (e.g. T5):** Translation aur summarization ke liye.
3. **Decoder-Only (e.g. GPT-1/2/3/4, Llama):** Auto-regressive text generation ke liye.
Hamara project **Decoder-Only architecture** implement karta hai.

---

### Q3: Auto-regressive Generation kya hoti hai?
**Answer:**
Auto-regressive ka matlab hai ki model ek baar me ek naya token predict karta hai. Fir wo naya token pichle input ke aage jod diya jata hai aur agla token predict karne ke liye wapas model me daala jata hai. Yeh loop tab tak chalta hai jab tak sentence poora na ho jaye ya `<EOS>` (End Of Sequence) token na aa jaye.

---

### Q4: Byte-Pair Encoding (BPE) Tokenization kaise kaam karta hai? (`bpe_merges.png`)
**Answer:**
- Pehle text ko individual characters me toda jata hai.
- BPE training corpus me sabse zyada repeat hone wale 2 characters ke pair ko dhoondta hai aur unhe merge karke ek naya token bana deta hai.
- *Example:* Agar `"l"` aur `"o"` bar-bar aa rahe hain, toh wo `"lo"` ban jayega. Fir `"lo"` aur `"w"` milkar `"low"` ban jayega.
- Isse common words single token ban jaate hain aur unknown words chote subwords me handle ho jaate hain.

---

### Q5: Token Embedding aur Positional Embedding me kya farak hai? (`embedding_lookup.png`)
**Answer:**
1. **Token Embedding:** Word ke semantic meaning ko capture karta hai (e.g. token ID 4998 $\rightarrow$ 768 floating numbers).
2. **Positional Embedding:** Word ke sentence me position (order) ko capture karta hai (e.g. 1st word, 2nd word).
Chunki Transformers saare words ko parallel me process karte hain (RNNs ki tarah sequentially nahi), isliye model ko batana padta hai ki kaun sa word pehle aaya aur kaun sa baad me. Final input = `Token Embedding + Positional Embedding`.

---

### Q6: Query ($Q$), Key ($K$), aur Value ($V$) ka physical meaning kya hai? (`attention_qkv.png`)
**Answer:**
Ek YouTube Search ka example lein:
- **Query ($Q$):** Jo aap search bar me type karte hain: *"Python tutorial"*.
- **Key ($K$):** YouTube par har video ka title/tag: *"Learn Python 2026"*.
- **Value ($V$):** Wo actual video jo aap play karke dekhte hain.
Model input vectors ko teen linear matrices ($W_q, W_k, W_v$) se multiply karke $Q, K, V$ banata hai. $Q$ aur $K$ ka dot product hota hai taaki pata chale kaun sa word kisse kitna related hai, aur fir utna hi weight uske $V$ ko diya jata hai.

---

### Q7: Scaled Dot-Product Attention ka formula aur scaling factor $\sqrt{d_k}$ kyun zaroori hai?
**Answer:**
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$
- **Scaling by $\sqrt{d_k}$:** Agar embedding dimension $d_k$ bada ho (e.g. 64 ya 128), toh dot product $Q K^T$ ki values bohot badi ho jaati hain.
- Badi values par `softmax` function saturate ho jata hai aur gradients lagbhag `0` ho jaate hain (**Vanishing Gradient Problem**).
- $\sqrt{d_k}$ se divide karne par values normalize rehti hain aur training stable hoti hai.

---

### Q8: Causal Masking (Look-Ahead Mask) kya hoti hai? (`causal_mask.png`)
**Answer:**
Generation ke waqt model ko cheating se rokne ke liye:
- Jab model 3rd word predict kar raha ho, toh use 4th aur 5th word dekhne ki permission nahi honi chahiye.
- Causal Mask ek lower-triangular matrix hoti hai jisme upper half me $-\infty$ (negative infinity) fill kar diya jata hai.
- Jab ispar `softmax` lagta hai, toh $-\infty$ zero ($0.0$) ban jata hai, jisse future tokens ka attention score 0 ho jata hai.

---

### Q9: Multi-Head Attention kya hota hai aur single head se behtar kyun hai? (`multihead.png`)
**Answer:**
Single attention head sirf ek perspective dekh sakta hai. Multi-Head Attention me hum embeddings ko multiple parts (e.g. 8 ya 12 heads) me split karte hain:
- Head 1: Noun aur Adjective ka relation dekhta hai.
- Head 2: Subject aur Verb ka agreement check karta hai.
- Head 3: Long-range dependency (paragraph context) dekhta hai.
Aakhiri me sabhi heads ke outputs ko concatenate karke linear projection se pass kiya jata hai.

---

### Q10: Residual Connections (Skip Highways) kya hain? (`residual_highway.png`)
**Answer:**
```python
x = x + self.attention(self.ln_1(x))
```
Jab neural network me 20-50 layers hoti hain, toh backpropagation ke waqt gradient piche aate-aate gayab ho jata hai. Residual connection input $x$ ko directly aage pass kar deta hai (skip highway). Isse gradients bina roke direct shuru ki layers tak flow kar sakte hain.

---

### Q11: Layer Normalization (LayerNorm) BatchNorm se kaise alag hai?
**Answer:**
- **BatchNorm:** Poore batch ke across statistics calculate karta hai (batch size par dependent hota hai, NLP me poorly perform karta hai).
- **LayerNorm:** Ek single sentence ke sabhi feature dimensions ke across mean aur variance calculate karke normalize karta hai. Isse har sequence independently normalize hoti hai chahe batch size kuch bhi ho.

---

### Q12: Feed-Forward Network (FFN) ka Transformer Block me kya role hai?
**Answer:**
Attention layer sirf words ke beech relation dhoondti hai (routing). Real "factual memory" aur patterns FFN layers me store hote hain. FFN me 2 linear transformations aur ek non-linear activation (GELU) hota hai:
$$\text{FFN}(x) = \text{GELU}(x W_1 + b_1) W_2 + b_2$$
Aam taur par FFN ka hidden dimension embedding dimension se 4x bada hota hai ($4 \times d_{\text{model}}$).

---

### Q13: ReLU ki jagah GELU (Gaussian Error Linear Unit) kyun use hota hai?
**Answer:**
ReLU negative values ko abruptly $0$ kar deta hai (Dying ReLU problem). GELU ek smooth, probabilistic curve follow karta hai jo choti negative values ko bhi thoda sa flow hone deta hai. Modern LLMs (GPT-3, Llama) me GELU standard activation hai.

---

### Q14: Transformer Block stacking kya hoti hai? (`transformer_block.png`)
**Answer:**
Ek single transformer block pattern extraction seekhta hai. Jab hum aise 12 ya 24 blocks ek ke upar ek stack karte hain:
- Lower Blocks: Basic syntax, characters aur grammar seekhte hain.
- Middle Blocks: Semantic meaning aur sentence context seekhte hain.
- Higher Blocks: Complex reasoning, logic aur factual knowledge capture karte hain.

---

### Q15: Logits kya hote hain aur final linear head kya karta hai? (`last_token_readout.png`)
**Answer:**
Transformer blocks ke aakhiri output vector ko vocabulary size (e.g. 50,257 tokens) ke linear layer se multiply kiya jata hai. Unadjusted raw scores ko **Logits** kehte hain. Logits batate hain ki vocabulary ka har word agle token ke roop me aane ka kitna chance rakhta hai.

---

### Q16: Softmax function logits ko probabilities me kaise badalta hai?
**Answer:**
$$\text{Softmax}(z_i) = \frac{e^{z_i}}{\sum_{j} e^{z_j}}$$
Softmax har logit ko exponential karke total sum se divide karta hai. Isse saare scores $0$ aur $1$ ke beech aa jaate hain aur unka total sum exact $1.0$ (100%) ban jata hai.

---

### Q17: Cross-Entropy Loss kya hota hai aur model loss kaise minimize karta hai? (`loss_intuition.png`)
**Answer:**
Cross-entropy naapta hai ki model ka predicted probability distribution real target word ke kitna kareeb hai:
$$\mathcal{L} = -\log(P(\text{correct\_token}))$$
Agar correct word aane ki probability model ne 99% di, toh loss lagbhag $0$ hoga. Agar model ne galat word ko high probability di, toh loss bohot high aayega. Backpropagation is loss ko gradient descent se kam karta hai.

---

### Q18: Training Loop me AdamW Optimizer aur Weight Decay ka kya kaam hai? (`training_loop.png`)
**Answer:**
AdamW gradient descent ka advanced version hai jo:
1. Momentum use karta hai (direction maintain rakhne ke liye).
2. Adaptive learning rates use karta hai har parameter ke liye.
3. **Weight Decay:** Model weights ko zyada bada hone se rokta hai taaki model training data ko blindly rat (overfit) na kare.

---

### Q19: Sliding Window Context kya hota hai? (`sliding_window.png`)
**Answer:**
Agar model ka maximum context length 1024 tokens hai, aur ab tak 1500 tokens generate ho chuke hain, toh model piche ke 476 tokens ko drop kar deta hai aur hamesha last 1024 tokens ki window slide karke agla word predict karta hai.

---

### Q20: Greedy Decoding vs Temperature Sampling me kya fark hai?
**Answer:**
- **Greedy Decoding:** Hamesha sabse high probability wale token (`argmax`) ko pick karna. Predictable aur repetitive ho sakta hai.
- **Temperature Sampling:** Probabilities ko temperature $T$ se scale karke randomly sample karna ($P_i \propto e^{z_i / T}$). Isse generation me natural creative variety aati hai.

---

### Q21: Top-k aur Top-p (Nucleus) Sampling generation ko kaise behtar banate hain?
**Answer:**
- **Top-k:** Model sirf top $k$ tokens (e.g. top 50) me se hi word chun sakta hai, baki bekar words cut ho jaate hain.
- **Top-p:** Cumulative probability threshold (e.g. 0.90). Top tokens ka sum jab tak 90% nahi ho jata, sirf unhe select kiya jata hai. Yeh dynamic pool maintain karta hai.

---

### Q22: Pre-training data format kaisa hota hai?
**Answer:**
Unsupervised continuous text file (e.g. Wikipedia articles ya books). Data ko input $X$ aur target $Y$ me split kiya jata hai jahan $Y$ hamesha $X$ se 1 token shifted hota hai:
- $X$: `["The", "sun", "rises", "in"]`
- $Y$: `["sun", "rises", "in", "the"]`

---

### Q23: PyTorch me Self-Attention Module ka minimal code kaisa dikhta hai?
**Answer:**
```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.q = nn.Linear(d_model, d_model, bias=False)
        self.k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Linear(d_model, d_model, bias=False)
        self.scale = math.sqrt(d_model)

    def forward(self, x, mask=None):
        Q, K, V = self.q(x), self.k(x), self.v(x)
        scores = (Q @ K.transpose(-2, -1)) / self.scale
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        weights = torch.softmax(scores, dim=-1)
        return weights @ V
```

---

### Q24: Model parameters count kaise calculate hota hai?
**Answer:**
Ek GPT model me:
- Embeddings: $V \times d_{\text{model}}$
- Attention: $4 \times d_{\text{model}}^2 \times \text{layers}$
- FFN: $8 \times d_{\text{model}}^2 \times \text{layers}$
PyTorch me total parameters dekhne ke liye:
```python
total_params = sum(p.numel() for p in model.parameters())
print(f"Total Parameters: {total_params:,}")
```

---

### Q25: Is Project ko study aur run karne ka best tareeqa kya hai?
**Answer:**
1. `images/` folder ke visual architectural diagrams (`pipeline.png`, `transformer_block.png`, `attention_qkv.png`) dekhein.
2. `Build_an_LLM_From_Scratch.ipynb` notebook ko step-by-step execute karein.
3. PyTorch tensor shapes (`[batch_size, seq_len, d_model]`) par dhyan dein ki har layer ke baad shape kaise transform ho rahi hai! 🎉
