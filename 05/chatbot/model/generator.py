# =============================================
# model/generator.py
# 역할: MiniGPT 모델 구조 + 학습 + 문장 생성
# =============================================

import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- 하이퍼파라미터 ----
BLOCK_SIZE = 16    # 한 번에 볼 수 있는 최대 글자 수
N_EMBD     = 128   # 글자를 몇 차원 숫자로 표현할지
N_HEAD     = 4     # 어텐션 헤드 수
N_LAYER    = 4     # 트랜스포머 블록 몇 개 쌓을지
DROPOUT    = 0.1   # 과적합 방지


# =============================================
# 토크나이저 — data.txt 글자로 자동 사전 구성
# =============================================

class Tokenizer:
    def __init__(self, text=''):
        self.PAD = '<PAD>'
        self.UNK = '<UNK>'
        self.EOS = '<EOS>'

        special      = [self.PAD, self.UNK, self.EOS]
        unique_chars = sorted(set(text))
        all_chars    = special + unique_chars

        self.stoi      = {c: i for i, c in enumerate(all_chars)}
        self.itos      = {i: c for c, i in self.stoi.items()}
        self.vocab_size = len(self.stoi)

    def encode(self, text):
        unk = self.stoi[self.UNK]
        return [self.stoi.get(c, unk) for c in text]

    def decode(self, ids):
        result = []
        for i in ids:
            token = self.itos.get(i, '')
            if token == self.EOS or token == '':
                break
            if token not in (self.PAD, self.UNK):
                result.append(token)
        return ''.join(result)


# 전역 토크나이저 (학습 시 갱신됨)
tokenizer = Tokenizer()


# =============================================
# Self-Attention
# =============================================

class SelfAttention(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.qkv  = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.proj = nn.Linear(n_embd, n_embd, bias=False)
        self.drop = nn.Dropout(DROPOUT)
        self.n_head = N_HEAD

    def forward(self, x):
        B, T, C = x.shape
        hd = C // self.n_head

        q, k, v = self.qkv(x).chunk(3, dim=-1)
        def sh(t): return t.view(B, T, self.n_head, hd).transpose(1, 2)
        q, k, v = sh(q), sh(k), sh(v)

        att  = q @ k.transpose(-2, -1) / hd**0.5
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=x.device))
        att  = att.masked_fill(~mask, float('-inf'))
        att  = self.drop(F.softmax(att, dim=-1))

        out = (att @ v).transpose(1, 2).reshape(B, T, C)
        return self.drop(self.proj(out))


# =============================================
# Transformer Block
# =============================================

class Block(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.ln1  = nn.LayerNorm(n_embd)
        self.attn = SelfAttention(n_embd)
        self.ln2  = nn.LayerNorm(n_embd)
        self.ff   = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd, bias=False),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd, bias=False),
            nn.Dropout(DROPOUT),
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))  # 잔차 연결!
        x = x + self.ff(self.ln2(x))    # 잔차 연결!
        return x


# =============================================
# MiniGPT — vocab_size를 인자로 받음!
# =============================================

class MiniGPT(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.vocab_size = vocab_size
        self.tok_emb = nn.Embedding(vocab_size, N_EMBD)
        self.pos_emb = nn.Embedding(BLOCK_SIZE, N_EMBD)
        self.drop    = nn.Dropout(DROPOUT)
        self.blocks  = nn.Sequential(*[Block(N_EMBD) for _ in range(N_LAYER)])
        self.ln_f    = nn.LayerNorm(N_EMBD)
        self.head    = nn.Linear(N_EMBD, vocab_size, bias=False)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.drop(
            self.tok_emb(idx) +
            self.pos_emb(torch.arange(T, device=idx.device))
        )
        x      = self.blocks(x)
        x      = self.ln_f(x)
        logits = self.head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, self.vocab_size),
                targets.view(-1)
            )
        return logits, loss


# =============================================
# 데이터 로드 — 토크나이저도 여기서 초기화!
# =============================================

def load_data(filepath, device):
    global tokenizer
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # data.txt 글자로 토크나이저 초기화
    tokenizer = Tokenizer(text)
    print(f'vocab 크기: {tokenizer.vocab_size}개 글자')

    data = torch.tensor(tokenizer.encode(text), dtype=torch.long, device=device)
    n    = int(0.9 * len(data))
    return data[:n], data[n:]


def get_batch(data, device, batch_size=32):
    ix = torch.randint(len(data) - BLOCK_SIZE - 1, (batch_size,))
    x  = torch.stack([data[i    : i + BLOCK_SIZE    ] for i in ix])
    y  = torch.stack([data[i + 1: i + BLOCK_SIZE + 1] for i in ix])
    return x, y


# =============================================
# 학습 함수
# =============================================

def train(filepath, device, steps=3000):
    # 1. 데이터 로드 (토크나이저 초기화됨)
    train_data, val_data = load_data(filepath, device)

    # 2. 토크나이저 초기화 후 모델 생성!
    model = MiniGPT(vocab_size=tokenizer.vocab_size).to(device)
    print(f'모델 파라미터: {sum(p.numel() for p in model.parameters()):,}개')

    # 3. AdamW 옵티마이저
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=3e-4,
        weight_decay=0.1
    )

    print(f'학습 시작! steps={steps}')
    model.train()

    for step in range(steps):
        x, y   = get_batch(train_data, device)
        _, loss = model(x, y)

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if step % 500 == 0 or step == steps - 1:
            model.eval()
            with torch.no_grad():
                vx, vy     = get_batch(val_data, device)
                _, val_loss = model(vx, vy)
            model.train()
            print(f'step {step:5d} | train {loss.item():.4f} | val {val_loss.item():.4f}')

    # 4. 모델 + 토크나이저 저장
    torch.save({
        'model_state': model.state_dict(),
        'vocab_size':  tokenizer.vocab_size,
        'stoi':        tokenizer.stoi,
        'itos':        tokenizer.itos,
    }, 'model/minigpt.pt')
    print('모델 저장 완료! → model/minigpt.pt')
    return model


# =============================================
# predict_next_token (과제 5-1)
# =============================================

def predict_next_token(model, text, device, temperature=0.8, top_k=50):
    model.eval()
    with torch.no_grad():
        ids = tokenizer.encode(text)[-BLOCK_SIZE:]
        idx = torch.tensor([ids], dtype=torch.long, device=device)

        logits, _ = model(idx)
        logits    = logits[0, -1, :] / temperature

        top_k     = min(top_k, logits.size(-1))
        top_vals  = torch.topk(logits, top_k).values
        logits[logits < top_vals[-1]] = float('-inf')

        probs    = F.softmax(logits, dim=-1)
        next_id  = torch.multinomial(probs, 1).item()
        return tokenizer.itos.get(next_id, '')


# =============================================
# generate (과제 5-2) — Autoregressive!
# =============================================

def generate(model, text, device, max_new_tokens=100, temperature=0.8, top_k=50):
    result = text
    for _ in range(max_new_tokens):
        next_char = predict_next_token(model, result, device, temperature, top_k)
        if next_char == tokenizer.EOS or next_char == '':
            break
        result += next_char
    return result


# =============================================
# 저장된 모델 불러오기
# =============================================

def load_model(filepath, device):
    global tokenizer
    checkpoint = torch.load(filepath, map_location=device)

    # 토크나이저 복원
    tokenizer.stoi      = checkpoint['stoi']
    tokenizer.itos      = checkpoint['itos']
    tokenizer.vocab_size = checkpoint['vocab_size']

    # 모델 복원
    model = MiniGPT(vocab_size=checkpoint['vocab_size']).to(device)
    model.load_state_dict(checkpoint['model_state'])
    model.eval()
    print('모델 불러오기 완료!')
    return model