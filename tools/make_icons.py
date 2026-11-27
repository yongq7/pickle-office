#!/usr/bin/env python3
"""뭐든다함 비서실 PWA 아이콘 생성기.

크림(#F7F1E6) 바탕에 금빛 왕관을 그린 정사각 아이콘을 만든다.
Android maskable 아이콘에서도 잘리지 않도록 그림은 중앙 80% 안전영역 안에 둔다.
"""
from PIL import Image, ImageDraw, ImageFilter

S = 2048                     # 슈퍼샘플링 캔버스
ZOOM = 1.22                  # 타일 대비 왕관 크기
CREAM_TOP = (255, 250, 240)
CREAM_BOT = (243, 234, 216)
INK = (122, 74, 22)

CX, CY = 1024, 1000          # 왕관 중심

# 왕관 실루엣 (2048 좌표)
BODY = [(500, 1200), (530, 760), (742, 930), (1024, 620),
        (1306, 930), (1518, 760), (1548, 1200)]
BALLS = [(530, 760, 74), (1024, 620, 82), (1518, 760, 74)]
BAND = (472, 1150, 1576, 1320)      # 좌상 x, y, 우하 x, y
BAND_R = 46


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    w, h = size
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return strip.resize((w, h), Image.BILINEAR)


def silhouette(scale=1.0):
    """왕관 전체(본체+띠+구슬) 실루엣 마스크. scale 은 중심 기준 확대/축소."""
    def T(p):
        return (CX + (p[0] - CX) * scale, CY + (p[1] - CY) * scale)

    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.polygon([T(p) for p in BODY], fill=255)
    x0, y0, x1, y1 = BAND
    d.rounded_rectangle([*T((x0, y0)), *T((x1, y1))], radius=BAND_R * scale, fill=255)
    for x, y, r in BALLS:
        px, py = T((x, y))
        rr = r * scale
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
    return m


def band_mask():
    x0, y0, x1, y1 = BAND
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 0, 0]) if False else None
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], radius=BAND_R, fill=255)
    return m


def paste_masked(base, color_img, mask):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(color_img, (0, 0), mask)
    return Image.alpha_composite(base, layer)


def crown_art():
    """왕관 그림(투명 배경) + 그림자."""
    art = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    art = paste_masked(art, Image.new("RGB", (S, S), INK), silhouette(1.014))   # 테두리
    art = paste_masked(art, vgrad((S, S), (252, 220, 138), (214, 148, 58)), silhouette(1.0))
    art = paste_masked(art, vgrad((S, S), (190, 112, 48), (132, 74, 22)), band_mask())

    d = ImageDraw.Draw(art)
    x0, y0, x1, y1 = BAND
    d.rounded_rectangle([x0 + 26, y0 + 16, x1 - 26, y0 + 34], radius=9, fill=(236, 174, 100, 190))
    d.rounded_rectangle([x0 + 22, y1 - 30, x1 - 22, y1 - 12], radius=9, fill=(96, 50, 14, 130))

    for jx in (676, 1024, 1372):
        jy, jr = 1235, 44
        d.ellipse([jx - jr, jy - jr, jx + jr, jy + jr], fill=(255, 247, 228, 255))
        d.ellipse([jx - jr, jy - jr, jx + jr, jy + jr], outline=(148, 90, 30, 230), width=8)
        d.ellipse([jx - jr + 14, jy - jr + 11, jx + 4, jy - 8], fill=(255, 255, 252, 225))

    for bx, by, br in BALLS:
        d.ellipse([bx - br, by - br, bx + br, by + br], outline=INK, width=10)
        d.ellipse([bx - br + br * .18, by - br + br * .14, bx + br * .05, by + br * .02],
                  fill=(255, 242, 208, 215))

    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow.paste((118, 68, 28, 105), (0, 40), silhouette(1.0))
    shadow = shadow.filter(ImageFilter.GaussianBlur(S * .016))
    return art, shadow


def zoom_layer(img, zoom):
    big = img.resize((round(S * zoom), round(S * zoom)), Image.LANCZOS)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(big, ((S - big.width) // 2, (S - big.height) // 2))
    return out


def background():
    bg = vgrad((S, S), CREAM_TOP, CREAM_BOT).convert("RGBA")
    vig = Image.new("L", (S, S), 255)
    hole = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hole).ellipse([-S * .22, -S * .34, S * 1.22, S * 1.10], fill=255)
    hole = hole.filter(ImageFilter.GaussianBlur(S * .11))
    vig = Image.composite(Image.new("L", (S, S), 150), vig, hole)
    bg = Image.composite(bg, Image.new("RGBA", (S, S), (238, 227, 206)), vig)
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * .13, S * .11, S * .87, S * .87], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(S * .08))
    return Image.composite(Image.new("RGBA", (S, S), (255, 252, 244)), bg, glow)


def build():
    bg = background()
    art, shadow = crown_art()
    bg = Image.alpha_composite(bg, zoom_layer(shadow, ZOOM))
    bg = Image.alpha_composite(bg, zoom_layer(art, ZOOM))

    out = bg.convert("RGB")
    out.resize((512, 512), Image.LANCZOS).save("icon-512.png", optimize=True)
    out.resize((192, 192), Image.LANCZOS).save("icon-192.png", optimize=True)
    out.resize((180, 180), Image.LANCZOS).save("apple-touch-icon.png", optimize=True)

    # maskable 미리보기(원형 크롭)
    small = out.resize((512, 512), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (512, 512), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 511, 511], fill=255)
    circ = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    circ.paste(small, (0, 0), mask)
    circ.save("tools/icon-maskable-preview.png")
    print("ok: icon-512.png, icon-192.png, apple-touch-icon.png, tools/icon-maskable-preview.png")


if __name__ == "__main__":
    build()
