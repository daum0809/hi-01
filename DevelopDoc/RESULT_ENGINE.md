# 결과 출력단 (담당 4) 인터페이스

## 역할
CSV 원본에서 KPI를 결정론적으로 계산하고, 계산 완료 데이터를 AI 분석 API 및 대시보드에 전달합니다.

## 고정 KPI
- CTR = clicks / impressions
- CVR = purchases / visits
- Cart Rate = add_to_cart / visits
- Cart→Purchase = purchases / add_to_cart
- ROAS = revenue / ad_spend
- CPC = ad_spend / clicks
- CPA = ad_spend / purchases
- AOV = revenue / purchases
- Revenue per Visit = revenue / visits

비율 지표는 내부 데이터에서 소수로 통일합니다. 예: 3.2% = 0.032.

## 3번 입력단과 계약
필수 권장 컬럼:
`date, product, channel, ad_spend, visits, purchases, revenue`

선택 컬럼:
`impressions, clicks, add_to_cart, category`

숫자 컬럼은 Number로 변환된 상태가 가장 좋지만 result-engine에서도 Number 변환을 방어적으로 수행합니다.

## 5번 출력단과 계약
`buildAnalysisPayload(rows)` 결과를 사용합니다.

핵심 구조:
- comparison.current: 최신월 KPI
- comparison.previous: 전월 KPI
- comparison.changes: 전월 대비 변화율(%)
- breakdowns.channel: 최신월 채널별 KPI
- breakdowns.product: 최신월 상품별 KPI

## OpenAI 연결
GitHub Pages 프론트에서 OpenAI API를 직접 호출하지 않습니다. API 키 노출 방지를 위해 서버/서버리스 함수에서 OpenAI를 호출해야 합니다.

서버에서는:
1. `buildAnalysisPayload(rows)` 결과 수신
2. `buildShopAnalysisPrompt(payload, question)` 생성
3. OpenAI 호출
4. JSON 응답 반환

## 완료 기준
- 같은 CSV는 항상 같은 KPI를 반환
- 0으로 나누는 경우 null 반환
- AI가 KPI를 재계산하지 않음
- 사실 / 가설 / 액션 / 한계가 분리된 JSON 반환
