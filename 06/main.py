"""
main.py - RAG FastAPI 서빙

RAG 파이프라인(검색 + Gemini 2.5 Flash 답변 생성)을 FastAPI로 감싸서
웹에서 사용할 수 있도록 한다.
- POST /ask: 질문을 받아 답변과 참고 문서를 반환
"""

from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import init_pipeline, ask

app = FastAPI(title="RAG API", description="KorQuAD 기반 한국어 RAG 질의응답 API")

# 서버 시작 시 파이프라인을 한 번만 초기화
init_pipeline()


class AskRequest(BaseModel):
    question: str
    k: int = 3


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


@app.get("/")
def root():
    return {"message": "RAG API가 정상적으로 실행 중입니다."}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    질문을 입력받아 관련 문서를 검색하고, Gemini 2.5 Flash로
    답변을 생성해서 반환하는 엔드포인트
    """
    result = ask(request.question, k=request.k)
    return AskResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)