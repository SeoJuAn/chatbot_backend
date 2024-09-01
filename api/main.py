import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import anthropic
import logging
import asyncio
import xml.etree.ElementTree as ET
import pandas as pd
import json
import time
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
import boto3

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


# class AIModelHandler:
#     def __init__(self):
#         self.bedrock_runtime = boto3.client("bedrock-runtime", region_name='us-east-1')


#     async def stream_generate_message(self, model, system_prompt, messages, max_tokens, temperature, top_p, top_k, stop_sequences):
#         if model.startswith("claude"):
#             async for char in self._stream_claude(system_prompt, messages, max_tokens, temperature, top_p, top_k, stop_sequences):
#                 yield char


#     async def _stream_claude(self, system_prompt, messages, max_tokens, temperature, top_p, top_k, stop_sequences):
#         prompt_config = {
#             "anthropic_version": "bedrock-2023-05-31",
#             "max_tokens": max_tokens,
#             "temperature": temperature,
#             "top_p": top_p,
#             "top_k":top_k,
#             "system": system_prompt,
#             "messages": self._format_messages(messages),
#             "stop_sequences": stop_sequences
#         }
#         model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
#         body = json.dumps(prompt_config)

#         response = self.bedrock_runtime.invoke_model_with_response_stream(
#             body=body,
#             modelId=model_id
#         )

#         for event in response.get("body"):
#             chunk = json.loads(event["chunk"]["bytes"])
#             if chunk['type'] == 'content_block_delta':
#                 if chunk['delta']['type'] == 'text_delta':
#                     text_chunk = chunk['delta']['text']
#                     for char in text_chunk:
#                         await asyncio.sleep(0.025)
#                         yield char



#     def _format_messages(self, messages):
#         formatted_messages = []
#         for i, msg in enumerate(messages):
#             role = "user" if i % 2 == 0 else "assistant"
#             formatted_messages.append({"role": role, "content": [{"type": "text", "text": msg}]})
#         return formatted_messages




# chat_core = AIModelHandler()



# @app.post("/chat")
# async def chat(request_data: ChatRequest):
#     messages = request_data.message

#     logger.info(request_data.message)

#     streaming = True
#     if streaming:
#         async def response_stream_generator():
#             async for char in chat_core.stream_generate_message('claude', '', messages, 2048, 0.7, 0.9, 40, []):
#                 yield char

#         return StreamingResponse(response_stream_generator(), media_type="text/event-stream")



@app.post("/chat")
async def chat(request: ChatRequest):
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
                    print(text, end="", flush=True)

                for text in stream.text_stream:
                    logging.info(f"text : {text}")
                    yield text
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            yield f"An error occurred: {str(e)}"


    logger.info(f"Received chat request: {request.message}")
    return StreamingResponse(generate_response(request.message), media_type="text/event-stream")

@app.post("/sql")
async def execute_sql(request: SQLRequest):
    logger.info(f"Received SQL request: {request.sql}")
    try:
        # 여기서는 테스트용 데이터를 반환합니다.
        # 실제 구현에서는 이 부분을 데이터베이스 쿼리 실행 로직으로 대체해야 합니다.

        # CSV 파일 경로
        airlines_file_path = './data/airlines.csv'
        airports_file_path = './data/airports.csv'
        flights_file_path = './data/flights.csv'

        # CSV 파일을 DataFrame으로 읽기
        airlines_df = pd.read_csv(airlines_file_path)
        airports_df = pd.read_csv(airports_file_path)
        flights_df = pd.read_csv(flights_file_path)

        response = client.beta.prompt_caching.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            temperature=0,
            system = """너는 주어진 데이터를 바탕으로 사용자의 쿼리 결과를 추출하는 AI야. 데이터는 DataFrame의 형태로 전달할 거고 하나의 DataFrame이 한 테이블이라고 생각하면 돼.
                        \n 직접 쿼리를 실행하는게 아니라 주어진 데이터를 바탕으로 쿼리를 실행했을 때 어떤 결과가 나올지 예상하는거야. 정확한 데이터가 아니어도 돼.
                        \n 하지만 절대 다른 말은 첨언하지 말고 반드시 아래 예시와 같은 형태로만 쿼리 결과 테이블을 표현해야해. 너가 준 결과를 바로 시각화할거라서 다른 텍스트가 있으면 안돼.
                        \n <결과 예시>
                        \n
                            [
                                {"days": "mon", "team": "data", "rev": 100, "cost": 10},
                                {"days": "tue", "team": "data", "rev": 1, "cost": 1},
                                {"days": "tue", "team": "cloud", "rev": 200, "cost": 20},
                                {"days": "wen", "team": "cloud", "rev": 2, "cost": 2},
                                {"days": "wen", "team": "dt", "rev": 300, "cost": 30},
                                {"days": "mon", "team": "dt", "rev": 3, "cost": 3}
                            ]
                        \n""" + f"""
                        \n\n(airlines 테이블)
                        \n{airlines_df}
                        \n\n(airports 테이블)
                        \n{airports_df}
                        \n\n(flights 테이블)
                        \n{flights_df}
                    """,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": request.sql,
                            "cache_control" : {"type" : "ephemeral"}
                        }
                    ]
                }
            ]
        )
        logging.info("Received response from Cashing Ver Anthropic API")

        content = response.content
        # TextBlock에서 텍스트 추출
        json_string = content[0].text

        # JSON 문자열을 Python 객체로 변환
        table = json.loads(json_string)


        logging.info(type(table))
        logging.info(table)


        # test_data = [
        #     {"days": "mon", "team": "data", "rev": 100, "cost": 10},
        #     {"days": "tue", "team": "data", "rev": 1, "cost": 1},
        #     {"days": "tue", "team": "cloud", "rev": 200, "cost": 20},
        #     {"days": "wen", "team": "cloud", "rev": 2, "cost": 2},
        #     {"days": "wen", "team": "dt", "rev": 300, "cost": 30},
        #     {"days": "mon", "team": "dt", "rev": 3, "cost": 3}
        # ]
        # logging.info(f"test_data : {test_data}")
        return JSONResponse(content=table)
    except Exception as e:
        logger.error(f"An error occurred while executing SQL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
