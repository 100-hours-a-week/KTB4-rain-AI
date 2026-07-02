"""
main.py - FastAPI 서빙

학습된 MiniGPT 모델을 FastAPI로 감싸서 웹에서 사용할 수 있도록 한다.
- POST /generate: 프롬프트를 받아 문장을 생성해서 반환
"""

from fastapi import FastAPI
from pydantic import BaseModel
from inference import load_model_and_tokenizer, generate

app = FastAPI(title="MiniGPT API", description="한국어 MiniGPT 문장 생성 API")

# 서버 시작 시 모델을 한 번만 로드 (요청마다 다시 로드하면 매우 느려짐)
MODEL_PATH = "minigpt.pt"
TOKENIZER_PATH = "tokenizer.model"

model, sp, device = load_model_and_tokenizer(MODEL_PATH, TOKENIZER_PATH)


class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.8
    top_k: int = 40


class GenerateResponse(BaseModel):
    prompt: str
    generated_text: str


@app.get("/")
def root():
    return {"message": "MiniGPT API가 정상적으로 실행 중입니다."}


@app.post("/generate", response_model=GenerateResponse)
def generate_text(request: GenerateRequest):
    """
    프롬프트를 입력받아 MiniGPT가 이어지는 문장을 생성해서 반환하는 엔드포인트
    """
    result = generate(
        model, sp, device,
        prompt=request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_k=request.top_k
    )
    return GenerateResponse(prompt=request.prompt, generated_text=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)