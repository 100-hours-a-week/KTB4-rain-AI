"""
inference.py - MiniGPT 문장 생성 (추론)

학습된 MiniGPT 모델(minigpt.pt)과 토크나이저를 불러와서
자기회귀적(autoregressive)으로 문장을 생성한다.
"""

import torch
import sentencepiece as spm
from model import MiniGPT


def load_model_and_tokenizer(model_path, tokenizer_path, vocab_size=16000, device=None):
    """
    학습된 모델과 토크나이저를 불러오는 함수

    Args:
        model_path: minigpt.pt 체크포인트 경로
        tokenizer_path: tokenizer.model 경로
        vocab_size: 어휘 사전 크기
        device: 'cuda' 또는 'cpu' (None이면 자동 감지)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # 토크나이저 로드
    sp = spm.SentencePieceProcessor()
    sp.load(tokenizer_path)

    # 모델 로드
    ckpt = torch.load(model_path, map_location=device)
    model = MiniGPT(vocab_size=vocab_size).to(device)
    model.load_state_dict(ckpt['model'])
    model.eval()

    print("모델 로드 완료!")
    return model, sp, device


def generate(model, sp, device, prompt, max_new_tokens=100, temperature=0.8, top_k=40):
    """
    프롬프트(시작 문장)를 받아서 이어지는 문장을 생성하는 함수

    Args:
        prompt: 생성을 시작할 입력 문장
        max_new_tokens: 생성할 최대 토큰 수
        temperature: 샘플링 온도 (높을수록 다양하고 낮을수록 결정적)
        top_k: top-k 샘플링 개수
    """
    tokens = sp.encode(prompt)
    x = torch.tensor([tokens], dtype=torch.long).to(device)

    with torch.no_grad():
        out = model.generate(
            x,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k
        )

    result = sp.decode(out[0].tolist())
    return result


if __name__ == "__main__":
    MODEL_PATH = "minigpt.pt"
    TOKENIZER_PATH = "tokenizer.model"

    model, sp, device = load_model_and_tokenizer(MODEL_PATH, TOKENIZER_PATH)

    # 테스트 문장 생성
    test_prompts = ["인공지능이란", "한국의 역사는", "삼성전자는"]

    for prompt in test_prompts:
        print(f"\n--- 입력: {prompt} ---")
        result = generate(model, sp, device, prompt)
        print(result)