"""
train.py - MiniGPT 학습 스크립트

토큰화된 데이터(tokens.bin)를 사용하여 MiniGPT 모델을 학습시킨다.
- Next Token Prediction 방식
- Optimizer: AdamW (lr=1e-3, cosine decay)
- Batch size: 128, Steps: 30,000
- 학습 장비: Google Colab A100 GPU
"""

import torch
import numpy as np
import os
import time
from model import MiniGPT


# ─── 설정 ───────────────────────────────
DRIVE_PATH = "/content/drive/MyDrive/MiniGPT"
TOKENS_PATH = f"{DRIVE_PATH}/tokens.bin"
CKPT_PATH = f"{DRIVE_PATH}/minigpt.pt"

VOCAB_SIZE = 16000
N_EMBD = 512
N_HEAD = 8
N_LAYER = 12
BLOCK_SIZE = 256
BATCH_SIZE = 128
MAX_STEPS = 30000
EVAL_EVERY = 500
SAVE_EVERY = 2000
LR = 1e-3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def get_batch(data, train_data, val_data, split, block_size, batch_size, device):
    """학습/검증용 배치를 랜덤하게 뽑아오는 함수"""
    d = train_data if split == 'train' else val_data
    ix = torch.randint(len(d) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy(d[i:i+block_size].astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy(d[i+1:i+block_size+1].astype(np.int64)) for i in ix])
    return x.to(device), y.to(device)


def train():
    print(f"사용 장치: {DEVICE}")

    # ─── 데이터 로드 ─────────────────────────
    print("데이터 로드 중...")
    data = np.memmap(TOKENS_PATH, dtype=np.uint16, mode='r')
    n = len(data)
    split_idx = int(n * 0.9)
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    print(f"학습 토큰: {len(train_data):,} | 검증 토큰: {len(val_data):,}")

    # ─── 모델 생성 ────────────────────────────
    model = MiniGPT(
        vocab_size=VOCAB_SIZE,
        n_embd=N_EMBD,
        n_head=N_HEAD,
        n_layer=N_LAYER,
        block_size=BLOCK_SIZE
    ).to(DEVICE)

    # 체크포인트 있으면 이어서 학습
    start_step = 0
    if os.path.exists(CKPT_PATH):
        print("체크포인트 발견! 이어서 학습...")
        ckpt = torch.load(CKPT_PATH, map_location=DEVICE)
        model.load_state_dict(ckpt['model'])
        start_step = ckpt['step']
        print(f"Step {start_step}부터 재개!")

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.1)
    scaler = torch.cuda.amp.GradScaler()  # 혼합 정밀도 학습

    # ─── 학습 루프 ────────────────────────────
    print(f"\n학습 시작! ({start_step} -> {MAX_STEPS} steps)")
    model.train()
    t0 = time.time()

    for step in range(start_step, MAX_STEPS):
        # 학습률 감소 (Cosine Decay)
        progress = step / MAX_STEPS
        lr = LR * (0.1 + 0.9 * (1 + np.cos(np.pi * progress)) / 2)
        for pg in optimizer.param_groups:
            pg['lr'] = lr

        # 배치 학습
        x, y = get_batch(data, train_data, val_data, 'train', BLOCK_SIZE, BATCH_SIZE, DEVICE)
        with torch.cuda.amp.autocast():
            _, loss = model(x, y)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        # 검증 및 출력
        if step % EVAL_EVERY == 0:
            model.eval()
            with torch.no_grad():
                xv, yv = get_batch(data, train_data, val_data, 'val', BLOCK_SIZE, BATCH_SIZE, DEVICE)
                with torch.cuda.amp.autocast():
                    _, val_loss = model(xv, yv)
            t1 = time.time()
            print(f"Step {step:5d} | train_loss: {loss.item():.4f} | val_loss: {val_loss.item():.4f} | {(t1-t0):.1f}s")
            t0 = time.time()
            model.train()

        # 체크포인트 저장
        if step % SAVE_EVERY == 0 and step > 0:
            torch.save({
                'step': step,
                'model': model.state_dict(),
                'val_loss': val_loss.item(),
            }, CKPT_PATH)
            print(f"체크포인트 저장! (step {step})")

    # 최종 저장
    torch.save({
        'step': MAX_STEPS,
        'model': model.state_dict(),
    }, CKPT_PATH)
    print("학습 완료!")


if __name__ == "__main__":
    train()