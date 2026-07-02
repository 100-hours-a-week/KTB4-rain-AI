"""
tokenizer.py - SentencePiece BPE 토크나이저 학습

한국어 위키백과 + FineWeb-2 한국어 데이터를 합쳐 만든 코퍼스(corpus.txt, 13.6GB)를
기반으로 BPE(Byte Pair Encoding) 방식의 서브워드 토크나이저를 학습시킨다.
- vocab_size=16,000
- 결과물: tokenizer.model, tokenizer.vocab
"""

import sentencepiece as spm
import os


def train_tokenizer(corpus_path, model_prefix, vocab_size=16000):
    """
    SentencePiece BPE 토크나이저를 학습시키는 함수

    Args:
        corpus_path: 학습에 사용할 코퍼스 텍스트 파일 경로
        model_prefix: 결과물 저장 경로/이름 (예: 'tokenizer' -> tokenizer.model, tokenizer.vocab 생성)
        vocab_size: 어휘 사전 크기 (기본값 16,000)
    """
    print("BPE 토크나이저 학습 시작...")

    spm.SentencePieceTrainer.train(
        input=corpus_path,
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        character_coverage=0.9995,   # 문자 커버리지 (한국어는 0.9995 권장)
        model_type="bpe",
        input_sentence_size=5000000,  # 500만 문장만 샘플링해서 학습 (속도 최적화)
        shuffle_input_sentence=True,
        pad_id=0,   # 패딩 토큰
        unk_id=1,   # 미등록 단어 토큰
        bos_id=2,   # 문장 시작 토큰
        eos_id=3,   # 문장 끝 토큰
    )

    print(f"토크나이저 학습 완료! {model_prefix}.model / {model_prefix}.vocab 생성됨")


def load_tokenizer(model_path):
    """학습된 토크나이저를 불러오는 함수"""
    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    return sp


if __name__ == "__main__":
    # 실제 학습 실행 (주의: corpus.txt는 13.6GB 대용량 파일이라 로컬에서 실행하려면
    # 파일이 있어야 함. 실제 학습은 Colab A100에서 수행했음)
    CORPUS_PATH = "/content/drive/MyDrive/MiniGPT/corpus.txt"
    MODEL_PREFIX = "/content/drive/MyDrive/MiniGPT/tokenizer"

    if os.path.exists(CORPUS_PATH):
        train_tokenizer(CORPUS_PATH, MODEL_PREFIX, vocab_size=16000)
    else:
        print(f"코퍼스 파일을 찾을 수 없습니다: {CORPUS_PATH}")
        print("이 스크립트는 Google Colab 환경(A100 GPU)에서 실행되었습니다.")