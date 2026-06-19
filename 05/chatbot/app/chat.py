# =============================================
# app/chat.py
# =============================================

from fastapi import APIRouter
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import state                                            #  main 대신 state에서 가져옴
from model.generator import predict_next_token, generate, tokenizer

router = APIRouter()

class ChatRequest(BaseModel):
    text: str
    max_new_tokens: int   = 100
    temperature:    float = 0.8
    top_k:          int   = 50

class NextWordResponse(BaseModel):
    next_word: str

class ChatResponse(BaseModel):
    input_text:  str
    output_text: str
    full_text:   str

@router.post("/api/next-word", response_model=NextWordResponse)
def next_word(req: ChatRequest):
    next_w = predict_next_token(state.model, req.text, state.device,   
                                req.temperature, req.top_k)
    return NextWordResponse(next_word=next_w)

@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    full = generate(state.model, req.text, state.device,               
                    req.max_new_tokens, req.temperature, req.top_k)
    return ChatResponse(
        input_text  = req.text,
        output_text = full[len(req.text):],
        full_text   = full
    )