import random
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import math


def generate_writing_image(digits=3):
    """Create an A4-sized image (300 DPI) with number-writing problems.

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

    title = f"{digits}자리 수 쓰기 연습 (숫자 → 한글)"
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
    low = 10 ** (digits - 1)
    high = 10 ** digits - 1

    # Ensure we pick unique numbers. If the digit-range is smaller than
    # the desired total, reduce total to the population size.
    population = high - low + 1
    if total > population:
        total = population

    problems = random.sample(range(low, high + 1), total)

    # layout: two columns, rows computed from actual total
    column_width = (width - 400) // 2
    start_x_left = 200
    start_x_right = 200 + column_width + 100
    start_y = 420

    rows_per_column = math.ceil(total / 2)
    bottom_margin = 200

    # compute spacing similarly to generate_problems
    bbox = draw.textbbox((0, 0), "0", font=problem_font)
    line_height = bbox[3] - bbox[1]
    available_space = height - start_y - bottom_margin
    denom = max(1, rows_per_column - 1)
    max_spacing = max(10, available_space // denom)

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
        number_str = str(n)

        if i < rows_per_column:
            x = start_x_left
            y = start_y + (i * problem_spacing)
        else:
            x = start_x_right
            y = start_y + ((i - rows_per_column) * problem_spacing)

        # Left: Number (큰 글씨)
        draw.text((x, y), number_str, fill='black', font=problem_font)

        # 오른쪽에 답란을 문제 바로 옆에 배치하도록 텍스트 폭을 측정
        number_bbox = draw.textbbox((0, 0), number_str, font=problem_font)
        number_width = number_bbox[2] - number_bbox[0]
        padding = 30
        desired_blank_x = x + number_width + padding

        # 답란이 컬럼 오른쪽을 벗어나지 않도록 최대값을 설정
        col_right = x + column_width - 40
        blank_x = min(desired_blank_x, col_right - 300)
        if blank_x < x + number_width + 10:
            # 안전장치: 너무 좁으면 기존 위치로 이동
            blank_x = x + column_width - 300

        draw.text((blank_x, y), "답: __________", fill='black', font=problem_font)

    return img


if __name__ == '__main__':
    # usage: python generate_writing.py <digits> [count]
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
        img = generate_writing_image(digits)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        if count == 1:
            filename = f"writing_problems_{digits}digits_{ts}.png"
        else:
            filename = f"writing_problems_{digits}digits_{ts}_{i+1}.png"
        path = os.path.join(output_dir, filename)
        img.save(path, 'PNG', dpi=(300, 300))
        saved.append(path)
        print(f"✓ 생성됨: {path}")

    # compute actual problems per image (may be reduced if digit-range < 36)
    low = 10 ** (digits - 1)
    high = 10 ** digits - 1
    used = min(36, high - low + 1)

    print(f"✓ 총 {len(saved)}개 이미지 생성 완료. 각 이미지에 {used}문제가 포함됩니다.")
