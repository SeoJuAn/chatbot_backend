import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatbot-frontend-dusky-alpha.vercel.app"],  # 실제 프론트엔드 URL로 변경하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수에서 API 키 가져오기
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise HTTPException(status_code=500, detail="API key not found")

client = anthropic.Anthropic(api_key=api_key)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    # try:
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
    #                         "text": "안녕?"
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
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    logging.info(f"Received default")
    return {"message": "Welcome to the chatbot API by SJA"}

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.message}")
    try:
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
        logging.info("Received response from Anthropic API")

        # content가 리스트인 경우 첫 번째 요소의 text를 반환
        if isinstance(response.content, list) and len(response.content) > 0:
            return {"response": response.content[0].text}
        # content가 딕셔너리인 경우 text 필드를 반환
        elif isinstance(response.content, dict) and 'text' in response.content:
            return {"response": response.content['text']}
        # 그 외의 경우 문자열로 변환하여 반환
        else:
            return {"response": str(response.content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Vercel 배포를 위해 if __name__ == "__main__": 부분은 제거됨