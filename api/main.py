import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import anthropic
import logging
import asyncio
import xml.etree.ElementTree as ET


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

log_level = 'INFO'
logger = logging.getLogger()
logger.setLevel(log_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
logger.addHandler(console_handler)

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatbot-frontend-bice.vercel.app"],  # 실제 프론트엔드 URL로 변경하세요
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

class SQLRequest(BaseModel):
    sql: str

@app.get("/")
def read_root():
    logging.info(f"Received default")
    return {"message": "Welcome to the chatbot API by SJA"}

# @app.post("/chat_cach")
# async def chat(request: ChatRequest):
#     logger.info(f"Received chat request: {request.message}")
#     try:
#         response = client.beta.prompt_caching.messages.create(
#             model="claude-3-5-sonnet-20240620",
#             max_tokens=1000,
#             temperature=0,
#             system = """너는 서주안을 도와주기 위해 만든 AI Assistant야. 최대한 사람들의 질문에 성심성의껏 답하도록해. 너는 Anthropic사의 Claude 3.5 모델을 사용해서 만들어졌어.
#                         \n""",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": request.message,
#                             "cache_control" : {"type" : "ephemeral"}
#                         }
#                     ]
#                 }
#             ]
#         )
#         logging.info("Received response from Anthropic API")

#         # content가 리스트인 경우 첫 번째 요소의 text를 반환
#         if isinstance(response.content, list) and len(response.content) > 0:
#             return {"response": response.content[0].text}
#         # content가 딕셔너리인 경우 text 필드를 반환
#         elif isinstance(response.content, dict) and 'text' in response.content:
#             return {"response": response.content['text']}
#         # 그 외의 경우 문자열로 변환하여 반환
#         else:
#             return {"response": str(response.content)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# XML 파일 읽기
tree = ET.parse('./prompt/table_info.xml')
root = tree.getroot()

# XML 내용을 문자열로 변환
xml_content = ET.tostring(root, encoding='unicode')

async def generate_response(message):
    try:
        with client.messages.stream(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=f"""너는 서주안을 도와주기 위해 만든 AI Assistant야. 최대한 사람들의 질문에 성심성의껏 답하도록해. 너는 Anthropic사의 Claude 3.5 모델을 사용해서 만들어졌어.
                       \n만약 사용자가 쿼리 작성이나 테이블에 대한 정보를 물어본다면 아래 정보를 참고해서 대답해줘. 다음은 비행, 공항, 항공사에 관한 테이블 정보야:
                       \n{xml_content}
                    """,
            messages=[
                {"role": "user", "content": message}
            ]
        ) as stream:
            for text in stream.text_stream:
                logging.info(f"text : {text}")
                yield text
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        yield f"An error occurred: {str(e)}"

 
@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Received chat request: {request.message}")
    return StreamingResponse(generate_response(request.message), media_type="text/plain")

@app.post("/sql")
async def execute_sql(request: SQLRequest):
    logger.info(f"Received SQL request: {request.sql}")
    try:
        # 여기서는 테스트용 데이터를 반환합니다.
        # 실제 구현에서는 이 부분을 데이터베이스 쿼리 실행 로직으로 대체해야 합니다.
        test_data = [
            {"mon": 1, "tue": 2, "wed": 3},
            {"mon": 4, "tue": 5, "wed": 6}
        ]
        return JSONResponse(content=test_data)
    except Exception as e:
        logger.error(f"An error occurred while executing SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
