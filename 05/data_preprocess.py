"""
data_preprocess.py - 위키백과 + FineWeb 데이터 다운로드 및 전처리

한국어 위키백과(647,897개 문서, 1.23GB)와 FineWeb-2 한국어 데이터
(3,000,000개 문서, 12.37GB)를 다운로드하고 정제하여 하나의 코퍼스
(corpus.txt, 총 13.6GB)로 합친다.
"""

import re
import os
from datasets import load_dataset


def clean_text(text):
    """텍스트 정제: 과도한 빈 줄 정리"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def download_wikipedia(output_path, min_length=100):
    """
    한국어 위키백과 데이터를 다운로드하고 텍스트 파일로 저장

    Args:
        output_path: corpus.txt를 저장할 경로
        min_length: 이 길이보다 짧은 문서는 제외
    """
    print("한국어 위키백과 다운로드 시작... 시간 좀 걸려요!")

    dataset = load_dataset(
        "wikimedia/wikipedia",
        "20231101.ko",
        split="train"
    )
    print(f"총 문서 수: {len(dataset):,}개")

    print("텍스트 추출 중...")
    with open(output_path, "w", encoding="utf-8") as f:
        for i, doc in enumerate(dataset):
            text = clean_text(doc['text'])
            if len(text) > min_length:
                f.write(text + "\n\n")

            if i % 50000 == 0:
                print(f"진행중: {i:,} / {len(dataset):,}")

    print("위키백과 전처리 완료!")


def download_fineweb(output_path, max_docs=3000000, min_length=100):
    """
    FineWeb-2 한국어 데이터를 다운로드하고 기존 corpus.txt에 이어붙임

    Args:
        output_path: 기존 corpus.txt 경로 (이어쓰기 모드로 추가됨)
        max_docs: 최대 다운로드할 문서 수
        min_length: 이 길이보다 짧은 문서는 제외
    """
    print("FineWeb-2 Korean 다운로드 시작... 시간 꽤 걸려요!")

    fineweb = load_dataset(
        "HuggingFaceFW/fineweb-2",
        name="kor_Hang",
        split="train",
        streaming=True  # 스트리밍 모드로 다운로드 (대용량 대응)
    )

    count = 0
    with open(output_path, "a", encoding="utf-8") as f:  # "a" = append(이어쓰기)
        for doc in fineweb:
            text = doc['text'].strip()
            if len(text) > min_length:
                f.write(text + "\n\n")
                count += 1
            if count % 100000 == 0:
                print(f"진행중: {count:,} / {max_docs:,}")
            if count >= max_docs:
                break

    print(f"FineWeb 전처리 완료! 총 {count:,}개 문서 추가됨")


def check_corpus_size(corpus_path):
    """생성된 코퍼스 파일 크기 확인"""
    size = os.path.getsize(corpus_path)
    size_gb = size / (1024 ** 3)
    print(f"최종 corpus.txt 크기: {size_gb:.2f} GB")
    return size_gb


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="위키백과 + FineWeb 코퍼스 구축")
    parser.add_argument("--output", type=str, default="/content/drive/MyDrive/MiniGPT/corpus.txt",
                         help="corpus.txt 저장 경로")
    parser.add_argument("--target-mb", type=int, default=None,
                         help="목표 용량(MB). 지정하지 않으면 전체 데이터 사용")
    parser.add_argument("--max-fineweb-docs", type=int, default=3000000,
                         help="FineWeb에서 가져올 최대 문서 수")
    args = parser.parse_args()

    # 1단계: 위키백과 다운로드
    download_wikipedia(args.output)

    # 2단계: FineWeb 추가 다운로드 (기존 파일에 이어붙임)
    download_fineweb(args.output, max_docs=args.max_fineweb_docs)

    # 3단계: 최종 크기 확인
    check_corpus_size(args.output)