# 뭐든다함 비서실 👑

대장님 전용 AI 비서실 웹앱입니다. 정적 페이지 하나(`index.html`)로 동작하고, 데이터는
Firebase Realtime Database에서 실시간으로 동기화됩니다. 승인된 계정으로 로그인해야만
들어갈 수 있습니다.

- **주소**: https://yongq7.github.io/pickle-office/
- **저장소**: https://github.com/yongq7/pickle-office

## 앱으로 설치 (PWA)

안드로이드 크롬에서 주소를 열고 **⋮ → 앱 설치**(또는 주소창의 설치 아이콘)를 누르면
홈 화면에 앱으로 설치됩니다. 주소창 없이 전체 화면(standalone)으로 열리고,
아이콘은 크림 바탕에 금빛 왕관입니다.

- 매니페스트: `manifest.webmanifest` (`display: standalone`, `start_url`·`scope` = `/pickle-office/`)
- 아이콘: `icon-192.png`(192×192, any) · `icon-512.png`(512×512, any + maskable) · `apple-touch-icon.png`
- 서비스워커: `sw.js` — 페이지·HTML은 네트워크 우선(새 배포 즉시 반영),
  아이콘·맵 이미지는 캐시 우선+뒤에서 갱신. Firebase·CDN 등 다른 출처 요청은 가로채지 않습니다.
- 아이콘을 다시 만들려면: `python3 tools/make_icons.py` (Pillow 필요)

## 구성

| 탭 | 하는 일 |
| --- | --- |
| 🗺️ 오피스 맵 | 클레이 3D 오피스 이미지 위에서 방(지휘실·대회의실·라운지)과 멤버 위치를 확인하고, 방 이름표를 눌러 바로 들어갑니다. |
| 💬 회의실 | 방별 채팅. 발신자는 **로그인한 계정으로 고정**되어(대장님·만능이·열매·클로드·GPT 중 하나) 본인 글은 오른쪽에 뜨고, `@멘션`으로 호출합니다. |
| 📋 작업실 | 작업 등록(담당자·우선순위)과 상태 변경(대기 → 실행중 → 완료), 삭제. |
| 📊 비서현황 | 비서 4인의 온라인/대기 상태, 현재 작업, 메모를 보고 바로 고칩니다. |
| 📝 메모 | 공유 메모 추가·완료 체크·삭제. |
| 🎁 당첨함 | 당첨된 경품·체험단을 한곳에 모아 사용/완료 여부를 실시간으로 체크. `전체` 보기에서는 **🛒 쿠팡체험단(리뷰 관리)** 과 **🎁 일반 당첨·경품** 이 섹션으로 나뉘고, 쿠팡체험단은 `리뷰대기 ↔ 리뷰완료`, 일반 경품은 `미사용 ↔ 사용완료`로 표시됩니다. 상단에 전체·미사용·완료 건수와 필터(전체 / 쿠팡체험단 / 일반 당첨 / 미사용·미완료 / 완료), 카드마다 상태 배지(눌러서 토글)·유효기간(만료 임박 강조)·쿠폰번호 복사·삭제, `＋ 당첨 추가` 폼(분류 선택 포함). 탭 라벨의 주황 배지는 미완료 건수. |

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
messages/{general|command|lounge}/{id}  { sender, name, emoji, role, text, ts }   // sender는 로그인 계정 키(yonggyu|manneungi|yeolmae|claude|gpt), 예전 값 '열매'는 'yeolmae'로 호환
tasks/{id}                              { title, owner, priority, status, ts }
memos/{id}                              { text, done, ts }
prizes/{id}                             { title, category(coupang|event), source, wonAt(YYYY-MM-DD), due(문자열), coupon, used, usedAt(ms), ts }
```

- `category`는 `coupang`(쿠팡체험단 — 리뷰 관리) 또는 `event`(일반 당첨·경품)입니다. 값이 없는 옛 항목은 `event`로 봅니다.
- `전체` 보기에서 🛒 쿠팡체험단과 🎁 일반 당첨이 섹션으로 나뉘고, 각 섹션 안에서 미사용(리뷰대기)이 먼저,
  같은 그룹에서는 `wonAt` 최신순으로 정렬됩니다.
  상태 배지·체크를 누르면 `used`/`usedAt`이 `PATCH`로 바로 저장됩니다.
- `due`에 `YYYY-MM-DD` 형식 날짜가 들어 있으면 남은 날짜(D-n)를 계산해 **7일 이내는 빨갛게**,
  기한이 지난 항목은 `기한 지남`으로 표시합니다. 날짜가 아닌 글(`문자/쿠폰 확인` 등)은 그대로 보여 줍니다.

## 파일

- `index.html` — 앱 전체 (HTML + CSS + JS). Firebase JS SDK v10 compat
  (`firebase-app-compat.js`, `firebase-auth-compat.js`)만 CDN에서 불러옵니다.
- `office-clay.png` — 오피스 맵 이미지
- `manifest.webmanifest` · `sw.js` · `icon-192.png` · `icon-512.png` · `apple-touch-icon.png` — PWA 설치용
- `tools/make_icons.py` — PWA 아이콘 생성 스크립트

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
