import random
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def number_to_korean(n: int) -> str:
    """Convert 1..9999 to Korean reading without spaces.

    Examples:
        213 -> 이백십삼
        100 -> 백
        10  -> 십
        101 -> 백일
    """
    if n == 0:
        return "영"

    digits = [(1000, '천'), (100, '백'), (10, '십'), (1, '')]
    num_names = {1: '일', 2: '이', 3: '삼', 4: '사', 5: '오', 6: '육', 7: '칠', 8: '팔', 9: '구'}

    parts = []
    remaining = n
    for place, place_name in digits:
        d = remaining // place
        remaining = remaining % place
        if d == 0:
            continue
        # For 10,100,1000: when digit is 1, omit '일' prefix (십, 백, 천)
        if place >= 10 and d == 1:
            parts.append(place_name)
        else:
            parts.append(num_names[d] + place_name)

    return ''.join(parts)


def generate_reading_image(digits=3):
    """Create an A4-sized image (300 DPI) with number-reading problems.

    Args:
        digits: number of digits for the random numbers (e.g., 3 -> 100..999)
    """
    width, height = 2480, 3508  # A4 @300dpi
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # fonts
    # Prefer Korean-capable fonts. Try Malgun (Windows), then Nanum, then fallback to default.
    problem_font_name = None
    try:
        title_font = ImageFont.truetype("malgun.ttf", 80)
        header_font = ImageFont.truetype("malgun.ttf", 50)
        problem_font = ImageFont.truetype("malgun.ttf", 60)
        problem_font_name = "malgun.ttf"
    except Exception:
        try:
            title_font = ImageFont.truetype("NanumGothic.ttf", 80)
            header_font = ImageFont.truetype("NanumGothic.ttf", 50)
            problem_font = ImageFont.truetype("NanumGothic.ttf", 60)
            problem_font_name = "NanumGothic.ttf"
        except Exception:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            problem_font = ImageFont.load_default()

    title = f"{digits}자리 수 읽기 연습 (숫자 → 한글)"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((width // 2 - title_width // 2, 100), title, fill='black', font=title_font)

    name_text = "이름: ________________"
    date_text = "날짜: ____년   ____월   ____일"
    draw.text((width // 4, 220), name_text, fill='black', font=header_font)
    draw.text((width * 3 // 4 - 420, 220), date_text, fill='black', font=header_font)

    draw.line([(200, 320), (width - 200, 320)], fill='black', width=3)

    # problems
    total = 36
    problems = []
    low = 10 ** (digits - 1)
    high = 10 ** digits - 1
    for _ in range(total):
        problems.append(random.randint(low, high))

    # layout: two columns x 18 rows
    column_width = (width - 400) // 2
    start_x_left = 200
    start_x_right = 200 + column_width + 100
    start_y = 420

    rows_per_column = 18
    bottom_margin = 200

    # compute spacing similarly to generate_problems
    bbox = draw.textbbox((0, 0), "0", font=problem_font)
    line_height = bbox[3] - bbox[1]
    available_space = height - start_y - bottom_margin
    max_spacing = max(10, available_space // (rows_per_column - 1))

    if hasattr(problem_font, 'size'):
        current_size = problem_font.size
        while line_height + 8 > max_spacing and current_size > 18:
            current_size -= 2
            try:
                if problem_font_name:
                    problem_font = ImageFont.truetype(problem_font_name, current_size)
                else:
                    problem_font = ImageFont.load_default()
                    break
            except Exception:
                problem_font = ImageFont.load_default()
                break
            bbox = draw.textbbox((0, 0), "0", font=problem_font)
            line_height = bbox[3] - bbox[1]

    problem_spacing = max_spacing

    for i in range(total):
        n = problems[i]
        korean = number_to_korean(n)

        if i < rows_per_column:
            x = start_x_left
            y = start_y + (i * problem_spacing)
        else:
            x = start_x_right
            y = start_y + ((i - rows_per_column) * problem_spacing)

        # Left: Korean reading (큰 글씨)
        draw.text((x, y), korean, fill='black', font=problem_font)

        # 오른쪽에 답란을 문제 바로 옆에 배치하도록 텍스트 폭을 측정
        korean_bbox = draw.textbbox((0, 0), korean, font=problem_font)
        korean_width = korean_bbox[2] - korean_bbox[0]
        padding = 30
        desired_blank_x = x + korean_width + padding

        # 답란이 컬럼 오른쪽을 벗어나지 않도록 최대값을 설정
        col_right = x + column_width - 40
        blank_x = min(desired_blank_x, col_right - 300)
        if blank_x < x + korean_width + 10:
            # 안전장치: 너무 좁으면 기존 위치로 이동
            blank_x = x + column_width - 300

        draw.text((blank_x, y), "답: __________", fill='black', font=problem_font)

    return img


if __name__ == '__main__':
    # usage: python generate_reading.py <digits> [count]
    if len(sys.argv) > 1:
        try:
            digits = int(sys.argv[1])
            if digits < 1 or digits > 4:
                print("⚠ 자릿수는 1~4 사이로 입력하세요. 기본값(3)을 사용합니다.")
                digits = 3
        except ValueError:
            print("⚠ 올바른 숫자를 입력하세요. 기본값(3)을 사용합니다.")
            digits = 3
    else:
        digits = 3

    if len(sys.argv) > 2:
        try:
            count = int(sys.argv[2])
            if count < 1:
                print("⚠ 개수는 1 이상이어야 합니다. 기본값(1)을 사용합니다.")
                count = 1
        except ValueError:
            print("⚠ 올바른 개수 숫자를 입력하세요. 기본값(1)을 사용합니다.")
            count = 1
    else:
        count = 1

    print(f"이미지 생성 중... ({digits}자리 문제, 이미지 수: {count})")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    saved = []
    for i in range(count):
        img = generate_reading_image(digits)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        if count == 1:
            filename = f"reading_problems_{digits}digits_{ts}.png"
        else:
            filename = f"reading_problems_{digits}digits_{ts}_{i+1}.png"
        path = os.path.join(output_dir, filename)
        img.save(path, 'PNG', dpi=(300, 300))
        saved.append(path)
        print(f"✓ 생성됨: {path}")

    print(f"✓ 총 {len(saved)}개 이미지 생성 완료. 각 이미지에 36문제가 포함됩니다.")
