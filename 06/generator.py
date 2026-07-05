"""
generator.py - RAG 답변 생성기 (Generator)

검색된 문서(retriever 결과)와 질문을 받아서, Gemini 2.5 Flash API로
문서에 근거한 답변을 생성한다.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 불러오기


def configure_gemini(api_key):
    """Gemini API 키를 설정하는 함수"""
    genai.configure(api_key=api_key)


def build_prompt(question, docs):
    """
    검색된 문서들과 질문을 하나의 프롬프트로 조합하는 함수

    Args:
        question: 사용자 질문
        docs: retriever가 검색해온 문서 리스트

    Returns:
        Gemini에게 전달할 프롬프트 문자열
    """
    context_text = "\n\n".join(
        [f"[문서 {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)]
    )

    prompt = f"""다음 문서들을 참고해서 질문에 답변해주세요.
문서에 없는 내용은 추측하지 말고, 모르면 모른다고 답변해주세요.

[참고 문서]
{context_text}

[질문]
{question}

[답변]"""

    return prompt


def generate_answer(question, docs, model_name="gemini-2.5-flash"):
    """
    검색된 문서를 근거로 Gemini 2.5 Flash가 답변을 생성하는 함수

    Args:
        question: 사용자 질문
        docs: retriever.py의 search()가 반환한 문서 리스트
        model_name: 사용할 Gemini 모델 이름

    Returns:
        생성된 답변 텍스트
    """
    prompt = build_prompt(question, docs)

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    import os
    from retriever import load_retriever, search

    # API 키는 환경변수에서 불러오는 것(코드에 직접 노출 금지)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    configure_gemini(GEMINI_API_KEY)

    retriever = load_retriever("faiss_index_local")

    question = "이순신의 장인은 누구인가?"
    docs = search(retriever, question)
    answer = generate_answer(question, docs)

    print(f"질문: {question}\n")
    print(f"답변: {answer}\n")
    print(f"--- 참고한 문서 {len(docs)}개 ---")
    for i, doc in enumerate(docs, 1):
        print(f"[문서 {i}] {doc.page_content[:100]}...")