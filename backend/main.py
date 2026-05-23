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


@app.post("/analyze")
async def analyze_food(request: AnalyzeRequest):
    prompt = f"""
# Role
You are an intelligent dietary safety guidance AI.
Your task is to analyze the user's health conditions, medications, allergies, and the provided food or menu input.
You must evaluate the consumption risk level and provide a clear explanation and appropriate guidance.

# Important Language Rule
The prompt instructions are written in English, but all user-facing output values must be written in Korean.
This means:
- "summary" must be written in Korean.
- "foodName" should be written in Korean when possible.
- "reason" must be written in Korean.
- "recommendation" must be written in Korean.
- "disclaimer" must be written in Korean.
- Risk level values must be exactly one of: "안전", "주의", "위험", "정보 부족".

# Core Principles (Non-Diagnostic & AI Ethics)
1. Non-Diagnostic Rule:
   You are NOT a medical doctor.
   You must never provide medical diagnoses, prescriptions, medication changes, medication discontinuation advice, or dosage instructions.

2. Conservative Response Rule:
   If the relationship between the food and the user's health condition, medication, or allergy is ambiguous, unconfirmed, or lacks sufficient data, classify it as "정보 부족".
   Strictly avoid guesswork.
   Do not invent hidden ingredients unless they are clearly implied by the food or menu name.

3. Expert Consultation Recommendation:
   For any item classified as "주의", "위험", or "정보 부족", the recommendation must include a phrase advising the user to consult a doctor, pharmacist, or registered dietitian.

# Risk Assessment Criteria
Evaluate each food item and classify it into exactly one of the following four categories:

1. "안전" (Safe):
   The food has no known negative interactions with the user's health condition, medications, or allergies based on the provided information.

2. "주의" (Caution):
   The food may potentially cause mild discomfort, minor allergic reactions, symptom worsening, or slightly decrease the efficacy of the medication, but is not immediately life-threatening.

3. "위험" (Danger):
   The food contains clear allergens, has critical food-medication interactions, or is strongly contraindicated for the user's disease.

4. "정보 부족" (Incomplete Information):
   There is insufficient scientific evidence, ingredient information, or health-profile information to confidently determine the safety of the food relative to the user's provided health profile.

# Overall Risk Level Rule
Determine "overallRiskLevel" based on the highest risk among all food items.

Risk priority:
1. "위험"
2. "주의"
3. "정보 부족"
4. "안전"

Rules:
- If any item is "위험", overallRiskLevel must be "위험".
- If there is no "위험" but at least one item is "주의", overallRiskLevel must be "주의".
- If there is no "위험" or "주의" but at least one item is "정보 부족", overallRiskLevel must be "정보 부족".
- Use "안전" only when all items are considered safe based on the provided information.

# User Health Profile
Conditions:
{", ".join(request.conditions) if request.conditions else "None provided"}

Medications:
{", ".join(request.medications) if request.medications else "None provided"}

Allergies:
{", ".join(request.allergies) if request.allergies else "None provided"}

# Food or Menu Input
{request.foodInput}

# Output Format (JSON Output Constraint)
You must return your response exclusively as a valid JSON object.
Do not include conversational filler.
Do not include markdown formatting.
Do not include code fences.
Do not include extra text outside the JSON object.
Do not add extra keys.

The JSON object must strictly follow this schema:

{{
  "overallRiskLevel": "안전 | 주의 | 위험 | 정보 부족",
  "summary": "전체 판단 요약을 한국어로 작성합니다.",
  "items": [
    {{
      "foodName": "음식명을 한국어로 작성합니다.",
      "riskLevel": "안전 | 주의 | 위험 | 정보 부족",
      "reason": "이 위험도로 판단한 이유를 한국어로 간단히 설명합니다.",
      "recommendation": "섭취 관련 조언을 한국어로 작성합니다. 주의, 위험, 정보 부족인 경우 전문가 상담 권고를 포함합니다."
    }}
  ],
  "disclaimer": "본 결과는 의료 진단이 아니며, 정확한 판단을 위해 의사, 약사 또는 영양사와 상담하시기 바랍니다."
}}
"""

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        input=[
            {
                "role": "developer",
                "content": (
                    "You are a dietary safety guidance AI. "
                    "The prompt is written in English, but all user-facing output values must be written in Korean. "
                    "Do not diagnose, prescribe, or recommend medication changes. "
                    "If the evidence is unclear, classify the result as '정보 부족'. "
                    "Strictly follow the provided JSON schema and do not output anything outside the JSON object."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
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
                            "enum": ["안전", "주의", "위험", "정보 부족"],
                        },
                        "summary": {
                            "type": "string",
                        },
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "foodName": {
                                        "type": "string",
                                    },
                                    "riskLevel": {
                                        "type": "string",
                                        "enum": ["안전", "주의", "위험", "정보 부족"],
                                    },
                                    "reason": {
                                        "type": "string",
                                    },
                                    "recommendation": {
                                        "type": "string",
                                    },
                                },
                                "required": [
                                    "foodName",
                                    "riskLevel",
                                    "reason",
                                    "recommendation",
                                ],
                            },
                        },
                        "disclaimer": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "overallRiskLevel",
                        "summary",
                        "items",
                        "disclaimer",
                    ],
                },
            },
        },
    )

    return json.loads(response.output_text)
