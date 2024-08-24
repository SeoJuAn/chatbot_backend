# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import anthropic

# app = FastAPI()

# # CORS 미들웨어 추가
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # React 앱의 주소
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# client = anthropic.Anthropic(api_key="")

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# async def chat(request: ChatRequest):
#     response = client.messages.create(
#         model="claude-3-5-sonnet-20240620",
#         max_tokens=1000,
#         temperature=0,
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": request.message
#                     }
#                 ]
#             }
#         ]
#     )
#     # content가 리스트인 경우 첫 번째 요소의 text를 반환
#     if isinstance(response.content, list) and len(response.content) > 0:
#         return {"response": response.content[0].text}
#     # content가 딕셔너리인 경우 text 필드를 반환
#     elif isinstance(response.content, dict) and 'text' in response.content:
#         return {"response": response.content['text']}
#     # 그 외의 경우 문자열로 변환하여 반환
#     else:
#         return {"response": str(response.content)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프론트엔드 배포 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수에서 API 키 가져오기
api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": request.message
                    }
                ]
            }
        ]
    )
    # content가 리스트인 경우 첫 번째 요소의 text를 반환
    if isinstance(response.content, list) and len(response.content) > 0:
        return {"response": response.content[0].text}
    # content가 딕셔너리인 경우 text 필드를 반환
    elif isinstance(response.content, dict) and 'text' in response.content:
        return {"response": response.content['text']}
    # 그 외의 경우 문자열로 변환하여 반환
    else:
        return {"response": str(response.content)}

# Vercel 배포를 위해 if __name__ == "__main__": 부분 제거