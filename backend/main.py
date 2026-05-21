import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI()

# React 개발 서버 주소 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AnalyzeRequest(BaseModel):
    conditions: list[str]
    medications: list[str]
    allergies: list[str]
    foodInput: str


@app.get("/")
def health_check():
    return {"message": "Diet guide backend is running"}

#임시 프롬포트(수정해야함)
@app.post("/analyze")
async def analyze_food(request: AnalyzeRequest):
    prompt = f"""
너는 식단 안전 안내 도우미다.

사용자의 질환, 복용 약물, 알레르기 정보를 보고 입력된 식단이
안전 / 주의 / 위험 / 정보 부족 중 어디에 해당하는지 판단한다.

중요 원칙:
1. 의료 진단이나 처방을 하지 않는다.
2. 약 복용 중단이나 용량 변경을 지시하지 않는다.
3. 확실하지 않은 음식 성분은 추측하지 말고 정보 부족으로 분류한다.
4. 알레르기와 직접 관련된 성분이 음식명에 명확히 포함되면 위험으로 분류한다.
5. 설명은 짧고 쉽게 작성한다.
6. 결과는 반드시 지정된 JSON 형식으로만 출력한다.

사용자 정보:
- 질환: {", ".join(request.conditions)}
- 복용 약물: {", ".join(request.medications)}
- 알레르기: {", ".join(request.allergies)}

식단 입력:
{request.foodInput}
"""

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        input=[
            {
                "role": "developer",
                "content": "너는 식단 안전 안내 도우미다. 진단이나 처방을 하지 말고, 반드시 JSON 형식으로만 답한다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "diet_safety_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "overallRiskLevel": {
                            "type": "string",
                            "enum": ["안전", "주의", "위험", "정보 부족"]
                        },
                        "summary": {
                            "type": "string"
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "foodName": {"type": "string"},
                                    "riskLevel": {
                                        "type": "string",
                                        "enum": ["안전", "주의", "위험", "정보 부족"]
                                    },
                                    "reason": {"type": "string"},
                                    "recommendation": {"type": "string"}
                                },
                                "required": [
                                    "foodName",
                                    "riskLevel",
                                    "reason",
                                    "recommendation"
                                ]
                            }
                        },
                        "disclaimer": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "overallRiskLevel",
                        "summary",
                        "items",
                        "disclaimer"
                    ]
                }
            }
        }
    )

    return json.loads(response.output_text)