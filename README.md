# 뭐든다함 비서실 👑

대장님 전용 AI 비서실 웹앱입니다. 정적 페이지 하나(`index.html`)로 동작하고, 데이터는
Firebase Realtime Database에서 실시간으로 동기화됩니다. 승인된 계정으로 로그인해야만
들어갈 수 있습니다.

- **주소**: https://yongq7.github.io/pickle-office/
- **저장소**: https://github.com/yongq7/pickle-office

## 구성

| 탭 | 하는 일 |
| --- | --- |
| 🗺️ 오피스 맵 | 클레이 3D 오피스 이미지 위에서 방(지휘실·대회의실·라운지)과 멤버 위치를 확인하고, 방 이름표를 눌러 바로 들어갑니다. |
| 💬 회의실 | 방별 채팅. 발신자(대장님·만능이·열매·클로드·GPT)를 골라 말하고 `@멘션`으로 호출합니다. |
| 📋 작업실 | 작업 등록(담당자·우선순위)과 상태 변경(대기 → 실행중 → 완료), 삭제. |
| 📊 비서현황 | 비서 4인의 온라인/대기 상태, 현재 작업, 메모를 보고 바로 고칩니다. |
| 📝 메모 | 공유 메모 추가·완료 체크·삭제. |

## 멤버

| 이름 | 역할 | 아이콘 |
| --- | --- | --- |
| 대장님 | 비서실 주인 | 👑 |
| 만능이 | 메인 비서 | 🐰 |
| 열매 | 협력 비서 | 🍓 |
| 클로드 | 분석 비서 | 🐱 |
| GPT | 전략 비서 | 🤖 |

## 로그인 (Firebase Auth)

- 페이지를 열면 먼저 잠금 카드가 뜨고, 로그인해야 앱 화면이 열립니다.
- **Google 계정으로 로그인**: `signInWithPopup`. 팝업이 막히는 모바일·인앱 브라우저에서는
  `signInWithRedirect`로 자동 전환합니다.
- **이메일/비밀번호 로그인**: 접이식 폼(자동 로봇 계정 등에서 사용).
- 로그인하면 `getIdToken()`으로 받은 ID 토큰을 모든 Realtime Database 요청에
  `?auth=<idToken>`으로 붙입니다(REST·EventSource 공통). 토큰은 `onIdTokenChanged`에서
  자동 갱신되고, 갱신되면 스트림을 다시 연결합니다.
- 권한 없는 계정으로 로그인하면 DB가 `401/403`을 돌려주고, 화면에
  "접근 권한이 없는 계정이에요" 안내와 로그아웃 버튼이 나타납니다.
- 헤더 오른쪽의 `로그아웃` 버튼으로 세션을 끝냅니다.

## 보안 규칙

Realtime Database 규칙이 잠겨 있어 로그인 토큰 없이는 읽기도 쓰기도 되지 않습니다.

```json
{
  "rules": {
    ".read":  "auth != null && (auth.token.email == 'yongq7@gmail.com' || auth.token.email == 'bot@pickle-office.local')",
    ".write": "auth != null && (auth.token.email == 'yongq7@gmail.com' || auth.token.email == 'bot@pickle-office.local')"
  }
}
```

- 허용 계정을 늘리려면 Firebase 콘솔의 Realtime Database → 규칙에서 이메일을 추가합니다.
- `bot@pickle-office.local`은 자동화(감시 스크립트)용 계정입니다. 비밀번호·서비스 계정
  파일은 **저장소에 절대 커밋하지 않습니다**(이 저장소에는 인증 비밀이 없습니다).

## 동기화 방식

- Firebase Realtime Database REST API (`https://pickle-office-hq-default-rtdb.firebaseio.com`)
- 실시간 스트림: `EventSource('.../messages/<room>.json?auth=...')` 등 Server-Sent Events
- 안정성 폴백: 5초 폴링 (스트림이 끊기면 상단 배지가 `폴링 모드`로 바뀝니다)

## 데이터 경로

```
agents/{manneungi|yeolmae|claude|gpt}   { name, role, status, task, memo }
messages/{general|command|lounge}/{id}  { sender, name, emoji, role, text, ts }
tasks/{id}                              { title, owner, priority, status, ts }
memos/{id}                              { text, done, ts }
```

## 파일

- `index.html` — 앱 전체 (HTML + CSS + JS). Firebase JS SDK v10 compat
  (`firebase-app-compat.js`, `firebase-auth-compat.js`)만 CDN에서 불러옵니다.
- `office-clay.png` — 오피스 맵 이미지

## 배포

- 라이브 주소: <https://yongq7.github.io/pickle-office/> (GitHub Pages, `gh-pages` 브랜치 루트)
- 고친 내용을 올릴 때:

  ```bash
  git push origin main
  git push origin main:gh-pages   # GitHub Pages가 보는 브랜치
  ```

- Pages 소스가 `main`이 아니라 `gh-pages` 브랜치로 설정되어 있습니다. 저장소
  **Settings → Pages → Build and deployment**에서 `main` / `/ (root)`로 바꾸면
  `gh-pages` 없이 `main`만 올려도 자동 반영됩니다.
