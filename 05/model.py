"""
model.py - MiniGPT 모델 정의

Decoder-only Transformer (GPT 계열) 구조로 직접 구현한 한국어 언어모델.
- n_layer=12, n_head=8, n_embd=512, block_size=256
- 총 파라미터 수: 약 54.3M (5,400만 개)
"""

import torch
import torch.nn as nn
import math


class MultiHeadAttention(nn.Module):
    """여러 방향으로 문장을 동시에 이해하는 장치 (Self-Attention)"""

    def __init__(self, n_embd, n_head):
        super().__init__()
        self.n_head = n_head
        self.n_embd = n_embd
        self.head_dim = n_embd // n_head

        self.qkv = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.proj = nn.Linear(n_embd, n_embd, bias=False)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.split(self.n_embd, dim=2)

        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        out = torch.nn.functional.scaled_dot_product_attention(
            q, k, v, is_causal=True, dropout_p=0.1 if self.training else 0.0
        )

        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(out)


class FeedForward(nn.Module):
    """정보를 더 깊이 처리하는 작은 신경망"""

    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd, bias=False),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd, bias=False),
            nn.Dropout(0.1),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    """Attention + FeedForward 한 묶음 (이 블록을 12개 쌓음)"""

    def __init__(self, n_embd, n_head):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = MultiHeadAttention(n_embd, n_head)
        self.ln2 = nn.LayerNorm(n_embd)
        self.ff = FeedForward(n_embd)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x


class MiniGPT(nn.Module):
    """전체 모델: 토큰 임베딩 -> 12개 TransformerBlock -> 다음 단어 예측"""

    def __init__(self, vocab_size, n_embd=512, n_head=8, n_layer=12, block_size=256):
        super().__init__()
        self.block_size = block_size

        self.transformer = nn.ModuleDict(dict(
            token_emb=nn.Embedding(vocab_size, n_embd),
            pos_emb=nn.Embedding(block_size, n_embd),
            drop=nn.Dropout(0.1),
            blocks=nn.ModuleList([
                TransformerBlock(n_embd, n_head) for _ in range(n_layer)
            ]),
            ln_f=nn.LayerNorm(n_embd),
        ))
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        device = idx.device

        pos = torch.arange(0, T, device=device)
        x = self.transformer.token_emb(idx) + self.transformer.pos_emb(pos)
        x = self.transformer.drop(x)

        for block in self.transformer.blocks:
            x = block(x)

        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=0
            )
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=0.8, top_k=40):
        """문장을 자기회귀적(autoregressive)으로 생성하는 함수"""
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature

            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = float('-inf')

            probs = torch.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


if __name__ == "__main__":
    vocab_size = 16000
    model = MiniGPT(vocab_size=vocab_size)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"총 파라미터 수: {total_params:,}개 ({total_params/1e6:.1f}M)")