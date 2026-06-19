# =============================================
# state.py
# 역할: 앱 전체에서 공유하는 model, device 보관
#       순환 임포트 없이 어디서든 가져다 쓸 수 있음
# =============================================

import torch

# 디바이스 설정 (GPU 있으면 GPU, 없으면 CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 모델은 main.py에서 load_model() 후 여기에 저장됨
model = None