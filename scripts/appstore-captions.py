#!/usr/bin/env python3
"""App Store 스크린샷에 캡션을 얹는다.

images/appstore/{iphone,ipad}/ 의 원본을 읽어
images/appstore/captioned/{iphone,ipad}/ 에 같은 이름으로 쓴다.
출력 크기는 원본과 같다 — App Store가 기기별 정해진 픽셀만 받기 때문이다.

색과 서체는 랜딩(index.html)의 --bg/--ink/--gold를 따른다.

    python3 scripts/appstore-captions.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "appstore"
OUT = SRC / "captioned"

BG = (250, 247, 242)  # --bg
INK = (58, 58, 58)  # --ink
GOLD = (201, 162, 39)  # --gold

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FONT_BOLD = 6  # ttc 안의 Bold 얼굴 인덱스

CAPTIONS = {
    "iphone": {
        "01-dashboard": "흩어진 계좌를 한눈에",
        "02-allocation": "목표에서 얼마나 벗어났는지",
        "03-health": "내 포트폴리오는 건강한가",
        "04-ranking": "계좌별·종목별 순위와 실시간 시세",
        "06-composition": "배당과 국가 분산까지",
        "07-projection": "1·3·5·10년 뒤 내 자산",
        "08-ai": "편중 진단과 성향별 목표 제안",
        "09-news": "보유 종목 뉴스와 증권사 리포트",
        "10-onboarding": "로그인 없이 둘러보기부터",
    },
    "ipad": {
        "01-dashboard": "넓은 화면에서는 더 넓게",
        "02-allocation": "목표에서 얼마나 벗어났는지",
        "03-ranking": "계좌별·종목별 순위와 실시간 시세",
        "04-ai": "편중 진단과 성향별 목표 제안",
        "05-health": "내 포트폴리오는 건강한가",
    },
}

# 기기별 여백 비율. 캡션 영역은 세로의 일정 비율을 쓰고, 남는 만큼 원본을 줄인다.
LAYOUT = {
    "iphone": {"shot_width_ratio": 0.848, "font_ratio": 0.052, "corner_ratio": 0.045},
    "ipad": {"shot_width_ratio": 0.872, "font_ratio": 0.030, "corner_ratio": 0.020},
}


def rounded(image: Image.Image, radius: int) -> Image.Image:
    """모서리를 깎아 알파를 가진 사본을 돌려준다."""
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, image.width - 1, image.height - 1), radius=radius, fill=255
    )
    out = image.convert("RGBA")
    out.putalpha(mask)
    return out


def render(src_path: Path, caption: str, layout: dict) -> Image.Image:
    shot = Image.open(src_path).convert("RGB")
    canvas_w, canvas_h = shot.size

    shot_w = int(canvas_w * layout["shot_width_ratio"])
    shot_h = round(shot.height * shot_w / shot.width)
    shot = shot.resize((shot_w, shot_h), Image.LANCZOS)
    shot = rounded(shot, int(shot_w * layout["corner_ratio"]))

    band_h = canvas_h - shot_h
    if band_h <= 0:
        raise ValueError(f"{src_path.name}: 캡션 영역이 남지 않는다 (band={band_h})")

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
    draw = ImageDraw.Draw(canvas)

    # 캡션이 길면 폭에 맞을 때까지 줄인다.
    size = int(canvas_w * layout["font_ratio"])
    while size > 8:
        font = ImageFont.truetype(FONT_PATH, size, index=FONT_BOLD)
        if draw.textlength(caption, font=font) <= canvas_w * 0.88:
            break
        size -= 2

    box = draw.textbbox((0, 0), caption, font=font)
    text_w, text_h = box[2] - box[0], box[3] - box[1]
    # 캡션 + 골드 밑줄을 캡션 영역 안에서 세로 가운데에 둔다.
    rule_gap = int(size * 0.55)
    rule_h = max(3, int(size * 0.075))
    block_h = text_h + rule_gap + rule_h
    top = (band_h - block_h) // 2

    draw.text(((canvas_w - text_w) // 2 - box[0], top - box[1]), caption, font=font, fill=INK)

    rule_w = int(size * 1.6)
    rule_y = top + text_h + rule_gap
    draw.rounded_rectangle(
        ((canvas_w - rule_w) // 2, rule_y, (canvas_w + rule_w) // 2, rule_y + rule_h),
        radius=rule_h // 2,
        fill=GOLD,
    )

    canvas.paste(shot, ((canvas_w - shot_w) // 2, band_h), shot)
    return canvas


def main() -> None:
    for device, captions in CAPTIONS.items():
        src_dir, out_dir = SRC / device, OUT / device
        out_dir.mkdir(parents=True, exist_ok=True)
        for stem, caption in captions.items():
            src_path = src_dir / f"{stem}.png"
            if not src_path.exists():
                print(f"건너뜀 {device}/{stem}.png — 원본 없음")
                continue
            out_path = out_dir / f"{stem}.png"
            render(src_path, caption, LAYOUT[device]).save(out_path)
            w, h = Image.open(out_path).size
            print(f"{device}/{stem}.png  {w}x{h}  “{caption}”")


if __name__ == "__main__":
    main()
