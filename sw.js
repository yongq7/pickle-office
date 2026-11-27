/* =========================================================
   뭐든다함 비서실 — Service Worker
   - 페이지/HTML: 네트워크 우선 (항상 최신 배포본, 실패하면 캐시)
   - 정적 자산(아이콘·맵 이미지·매니페스트): 캐시 우선 + 뒤에서 갱신
   - Firebase/CDN 등 다른 출처 요청은 절대 가로채지 않는다
     (실시간 SSE·인증 통신 방해 금지)
   ========================================================= */
const VERSION = 'v3';
const CACHE = 'pickle-office-' + VERSION;

/* 설치 직후 오프라인에서도 잠금 화면·아이콘이 뜨도록 미리 담아 둔다 */
const CORE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
  './office-clay.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    /* 하나가 실패해도 설치는 계속 (office-clay.png 는 용량이 커서 실패 가능) */
    await Promise.all(CORE.map(async (url) => {
      try {
        const res = await fetch(new Request(url, { cache: 'reload' }));
        if (res && res.ok) await cache.put(url, res.clone());
      } catch (err) {
        /* 무시: 오프라인 캐시는 보너스일 뿐 */
      }
    }));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((k) => k.startsWith('pickle-office-') && k !== CACHE)
      .map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

async function networkFirst(request, fallbackKey) {
  const cache = await caches.open(CACHE);
  try {
    /* no-cache: 브라우저 HTTP 캐시(깃허브 페이지스 10분)에 기대지 않고
       매번 서버에 물어 최신 배포본을 받는다. 바뀐 게 없으면 304로 가볍다. */
    let fresh;
    try {
      fresh = await fetch(request.url, {
        cache: 'no-cache',
        credentials: 'same-origin',
        redirect: 'follow'
      });
    } catch (e) {
      fresh = await fetch(request);
    }
    if (fresh && fresh.ok) cache.put(request, fresh.clone()).catch(() => {});
    return fresh;
  } catch (err) {
    const hit = await cache.match(request);
    if (hit) return hit;
    if (fallbackKey) {
      const fb = await cache.match(fallbackKey);
      if (fb) return fb;
    }
    return new Response(
      '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#f7f1e6;' +
      'font-family:system-ui,-apple-system,\'Noto Sans KR\',sans-serif;color:#5a3a22;text-align:center;padding:24px">' +
      '<div><div style="font-size:40px">👑</div><h1 style="font-size:17px;margin:12px 0 6px">오프라인 상태예요</h1>' +
      '<p style="font-size:13px;line-height:1.6;margin:0;color:#8a7860">인터넷에 연결되면 자동으로 다시 열려요.<br>' +
      '연결 후 새로고침해 주세요.</p></div></body>',
      { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    );
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  const fetching = fetch(request).then((res) => {
    if (res && res.ok) cache.put(request, res.clone()).catch(() => {});
    return res;
  }).catch(() => null);
  if (hit) return hit;
  const res = await fetching;
  if (res) return res;
  return new Response('', { status: 504, statusText: 'offline' });
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  /* 같은 출처(깃허브 페이지)만 다룬다. Firebase·구글 폰트·CDN 은 그대로 통과. */
  if (url.origin !== self.location.origin) return;
  /* Range 요청(영상·오디오 탐색)은 캐시가 깨뜨릴 수 있어 통과 */
  if (request.headers.get('range')) return;

  /* 페이지 이동(주소 열기·새로고침)은 네트워크 우선 → 새 배포가 바로 반영 */
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, './index.html'));
    return;
  }

  /* HTML 문서 요청도 네트워크 우선 */
  if (request.destination === 'document') {
    event.respondWith(networkFirst(request, './index.html'));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});
