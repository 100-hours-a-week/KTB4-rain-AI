# =============================================
# main.py
# =============================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

import state                          # ✨ state 먼저 임포트
from app.chat import router
from model.generator import load_model

app = FastAPI(title="MiniGPT 한국어 챗봇")

# 모델 불러와서 state.model에 저장
if os.path.exists('model/minigpt.pt'):
    state.model = load_model('model/minigpt.pt', state.device)
    print('저장된 모델 불러오기 완료!')
else:
    print('저장된 모델 없음! 먼저 학습을 실행하세요.')

app.include_router(router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload= False)