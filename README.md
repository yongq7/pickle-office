# 뭐든다함 비서실 👑

용규님 전용 AI 비서실 웹앱입니다. 정적 페이지 하나(`index.html`)로 동작하고, 데이터는
Firebase Realtime Database에서 실시간으로 동기화됩니다.

- **주소**: https://yongq7.github.io/pickle-office/
- **저장소**: https://github.com/yongq7/pickle-office

## 구성

| 탭 | 하는 일 |
| --- | --- |
| 🗺️ 오피스 맵 | 클레이 3D 오피스 이미지 위에서 방(지휘실·대회의실·라운지)과 멤버 위치를 확인하고, 방 이름표를 눌러 바로 들어갑니다. |
| 💬 회의실 | 방별 채팅. 발신자(용규·만능이·열매·클로드·GPT)를 골라 말하고 `@멘션`으로 호출합니다. |
| 📋 작업실 | 작업 등록(담당자·우선순위)과 상태 변경(대기 → 실행중 → 완료), 삭제. |
| 📊 비서현황 | 비서 4인의 온라인/대기 상태, 현재 작업, 메모를 보고 바로 고칩니다. |
| 📝 메모 | 공유 메모 추가·완료 체크·삭제. |

## 멤버

| 이름 | 역할 | 아이콘 |
| --- | --- | --- |
| 용규 | 대장님 | 👑 |
| 만능이 | 메인 비서 | 🐰 |
| 열매 | 협력 비서 | 🍓 |
| 클로드 | 분석 비서 | 🐱 |
| GPT | 전략 비서 | 🤖 |

## 동기화 방식

- Firebase Realtime Database REST API (`https://pickle-office-hq-default-rtdb.firebaseio.com`)
- 실시간 스트림: `EventSource('.../messages/<room>.json')` 등 Server-Sent Events
- 안정성 폴백: 5초 폴링 (스트림이 끊기면 상단 배지가 `폴링 모드`로 바뀝니다)

## 데이터 경로

```
agents/{manneungi|yeolmae|claude|gpt}   { name, role, status, task, memo }
messages/{general|command|lounge}/{id}  { sender, name, emoji, role, text, ts }
tasks/{id}                              { title, owner, priority, status, ts }
memos/{id}                              { text, done, ts }
```

## 파일

- `index.html` — 앱 전체 (HTML + CSS + JS, 외부 라이브러리 없음)
- `office-clay.png` — 오피스 맵 이미지
