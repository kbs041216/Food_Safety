# Frontend Guide

이 문서는 React 프론트엔드 담당자가 FastAPI 백엔드와 연동하기 위해 필요한 정보를 정리한 문서입니다.

프론트엔드는 사용자의 질환, 복용 약물, 알레르기 정보와 식단 입력값을 백엔드로 전송하고, 백엔드가 반환한 분석 결과를 화면에 출력합니다.

---

## 1. 전체 구조

```text
React Frontend
        ↓
FastAPI Backend
        ↓
OpenAI API
        ↓
JSON Response
        ↓
React Result Card
```

프론트엔드는 OpenAI API를 직접 호출하지 않습니다.  
반드시 FastAPI 백엔드의 `/analyze` API로 요청을 보내야 합니다.

---

## 2. 백엔드 실행 주소

로컬 개발 환경 기준 백엔드 주소는 다음과 같습니다.

```text
http://localhost:8000
```

FastAPI 문서 페이지는 아래 주소에서 확인할 수 있습니다.

```text
http://localhost:8000/docs
```

---

## 3. 사용할 API

### POST `/analyze`

사용자의 건강 정보와 식단 입력값을 백엔드로 보내면, 백엔드가 식단 안전성을 분석한 결과를 JSON으로 반환합니다.

요청 주소:

```text
http://localhost:8000/analyze
```

---

## 4. 프론트엔드 입력 항목

프론트엔드에서는 사용자가 아래 정보를 입력할 수 있게 구현합니다.

### 질환 선택

```js
const conditionOptions = ["없음", "고혈압", "당뇨", "신장질환", "통풍"];
```

### 복용 약물 선택

```js
const medicationOptions = ["없음", "와파린", "스타틴", "MAOI 항우울제", "갑상선약"];
```

### 알레르기 선택

```js
const allergyOptions = ["없음", "땅콩", "우유", "계란", "새우"];
```

### 식단 입력

사용자가 자연어로 음식 또는 식단을 입력합니다.

예시:

```text
오늘 라면이랑 땅콩버터 샌드위치 먹어도 돼?
```

---

## 5. 요청 JSON 형식

프론트엔드는 `/analyze` API에 아래 형식으로 요청을 보냅니다.

```json
{
  "conditions": ["고혈압"],
  "medications": ["없음"],
  "allergies": ["땅콩"],
  "foodInput": "오늘 라면이랑 땅콩버터 샌드위치 먹어도 돼?"
}
```

### 필드 설명

| 필드명 | 타입 | 설명 |
|---|---|---|
| conditions | string[] | 사용자가 선택한 질환 목록 |
| medications | string[] | 사용자가 선택한 복용 약물 목록 |
| allergies | string[] | 사용자가 선택한 알레르기 목록 |
| foodInput | string | 사용자가 자연어로 입력한 음식 또는 식단 |

질환, 약물, 알레르기가 없는 경우에는 `["없음"]`으로 보내면 됩니다.

---

## 6. 응답 JSON 형식

백엔드는 아래 형식으로 응답합니다.

```json
{
  "overallRiskLevel": "위험",
  "summary": "라면은 고혈압이 있는 경우 주의가 필요하고, 땅콩버터 샌드위치는 땅콩 알레르기와 관련되어 위험할 수 있습니다.",
  "items": [
    {
      "foodName": "라면",
      "riskLevel": "주의",
      "reason": "라면은 일반적으로 나트륨 함량이 높아 고혈압이 있는 경우 주의가 필요합니다.",
      "recommendation": "국물 섭취를 줄이고 섭취 빈도를 조절하는 것이 좋습니다."
    },
    {
      "foodName": "땅콩버터 샌드위치",
      "riskLevel": "위험",
      "reason": "땅콩 알레르기가 있는 경우 땅콩버터 섭취는 위험할 수 있습니다.",
      "recommendation": "섭취를 피하고 필요하면 전문가와 상담하세요."
    }
  ],
  "disclaimer": "이 서비스는 진단이나 처방을 제공하지 않으며, 정확한 판단은 의사 또는 약사와 상담해야 합니다."
}
```

---

## 7. 응답 필드 설명

| 필드명 | 타입 | 설명 |
|---|---|---|
| overallRiskLevel | string | 전체 식단의 최종 위험도 |
| summary | string | 전체 식단에 대한 요약 설명 |
| items | array | 음식별 분석 결과 목록 |
| foodName | string | 분석된 음식명 |
| riskLevel | string | 해당 음식의 위험도 |
| reason | string | 위험도 판단 이유 |
| recommendation | string | 권장 행동 |
| disclaimer | string | 의료 진단 및 처방이 아님을 알리는 문구 |

---

## 8. 위험도 값

위험도는 아래 4개 값 중 하나로 반환됩니다.

```js
const riskLevels = ["안전", "주의", "위험", "정보 부족"];
```

### 추천 UI 색상

| 위험도 | 추천 색상 |
|---|---|
| 안전 | 초록색 |
| 주의 | 노란색 또는 주황색 |
| 위험 | 빨간색 |
| 정보 부족 | 회색 또는 파란색 |

---

## 9. React fetch 예시

```js
const analyzeDiet = async () => {
  const response = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      conditions: selectedConditions,
      medications: selectedMedications,
      allergies: selectedAllergies,
      foodInput: foodInput,
    }),
  });

  const data = await response.json();
  setResult(data);
};
```

---

## 10. 화면 출력 예시

프론트엔드에서는 결과를 카드 형태로 보여주면 됩니다.

```text
전체 판정: 위험

요약:
라면은 고혈압이 있는 경우 주의가 필요하고, 땅콩버터 샌드위치는 땅콩 알레르기와 관련되어 위험할 수 있습니다.

[라면]
판정: 주의
이유: 라면은 일반적으로 나트륨 함량이 높아 고혈압이 있는 경우 주의가 필요합니다.
권장 행동: 국물 섭취를 줄이고 섭취 빈도를 조절하는 것이 좋습니다.

[땅콩버터 샌드위치]
판정: 위험
이유: 땅콩 알레르기가 있는 경우 땅콩버터 섭취는 위험할 수 있습니다.
권장 행동: 섭취를 피하고 필요하면 전문가와 상담하세요.

주의 문구:
이 서비스는 진단이나 처방을 제공하지 않으며, 정확한 판단은 의사 또는 약사와 상담해야 합니다.
```

---

## 11. 프론트엔드 구현 체크리스트

- [ ] 질환 선택 UI 구현
- [ ] 복용 약물 선택 UI 구현
- [ ] 알레르기 선택 UI 구현
- [ ] 식단 자연어 입력창 구현
- [ ] 분석하기 버튼 구현
- [ ] `/analyze` API 요청 연결
- [ ] 로딩 상태 표시
- [ ] 오류 발생 시 안내 문구 표시
- [ ] 전체 판정 출력
- [ ] 음식별 결과 카드 출력
- [ ] 위험도별 색상 구분
- [ ] disclaimer 출력

---

## 12. 주의사항

- 프론트엔드는 OpenAI API 키를 절대 사용하지 않습니다.
- OpenAI API 호출은 FastAPI 백엔드에서만 처리합니다.
- 백엔드 서버가 실행 중이어야 프론트에서 API 요청이 가능합니다.
- 로컬 개발 시 백엔드는 `http://localhost:8000`에서 실행됩니다.
- 프론트 개발 서버가 Vite 기준 `http://localhost:5173`이면 CORS 설정이 맞아야 합니다.
