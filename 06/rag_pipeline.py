"""
rag_pipeline.py - RAG 파이프라인 통합

retriever(검색)와 generator(답변 생성)를 하나로 연결해서,
질문을 넣으면 검색부터 답변까지 한 번에 처리하는 함수를 제공한다.
"""

import os
from dotenv import load_dotenv

from retriever import load_retriever, search
from generator import configure_gemini, generate_answer

load_dotenv()

FAISS_PATH = "faiss_index_local"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 전역으로 한 번만 로드 (요청마다 다시 로드하면 매우 느려짐)
_retriever = None


def init_pipeline():
    """
    파이프라인 초기화: 임베딩 모델, FAISS 저장소, Gemini API 설정을
    한 번만 로드한다. (서버 시작 시 1회 호출)
    """
    global _retriever
    configure_gemini(GEMINI_API_KEY)
    _retriever = load_retriever(FAISS_PATH)
    print("RAG 파이프라인 초기화 완료!")


def ask(question, k=3):
    """
    질문을 받아서 검색 -> 답변 생성까지 한 번에 처리하는 함수

    Args:
        question: 사용자 질문
        k: 검색할 문서 개수 (기본 3개)

    Returns:
        dict: {"question": ..., "answer": ..., "sources": [...]}
    """
    if _retriever is None:
        raise RuntimeError("파이프라인이 초기화되지 않았습니다. init_pipeline()을 먼저 호출하세요.")

    docs = search(_retriever, question)
    answer = generate_answer(question, docs)

    return {
        "question": question,
        "answer": answer,
        "sources": [doc.page_content[:200] for doc in docs]
    }


if __name__ == "__main__":
    init_pipeline()

    test_questions = [
        "이순신의 장인은 누구인가?",
        "이순신은 누구인가?",
    ]

    for q in test_questions:
        result = ask(q)
        print(f"\n질문: {result['question']}")
        print(f"답변: {result['answer']}")
        print(f"참고 문서 {len(result['sources'])}개")