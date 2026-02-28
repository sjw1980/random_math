import random
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def generate_subtraction_problem(difficulty=5):
    """뺄셈 문제 생성 (초등학교 1~2학년 수준 기준)
    
    Args:
        difficulty: 난이도 (1-10)
            1: 극쉬움 (1~9, 1자리 뺄셈, 받아내림 없음)
            2: 쉬움-하 (1~20, 받아내림 없음)
            3: 쉬움-상 (1~30, 받아내림 없음, 일의 자리 a >= b)
            4: 특별 (10 배수 또는 10~19에서 1자리 빼기)
            5-6: 보통 (1~100, 2개 숫자, 받아내림 가능)
            7-10: 어려움 (50~100, 3개 숫자 연속 뺄셈)
    
    Returns:
        list: 뺄셈할 숫자 목록 (첫 번째가 가장 큰 수)
    """
    if difficulty <= 1:
        # 극쉬움: 1~9 범위, 받아내림 없음 (단순 1자리 뺄셈)
        a = random.randint(2, 9)
        b = random.randint(1, a)
        numbers = [a, b]

    elif difficulty == 2:
        # 쉬움-하: 1~20 범위, 받아내림 없음
        # a의 일의 자리 >= b의 일의 자리
        while True:
            a = random.randint(2, 20)
            b = random.randint(1, a)
            if (a % 10) >= (b % 10):
                break
        numbers = [a, b]

    elif difficulty == 3:
        # 쉬움-상: 1~30, 받아내림 없음 (일의 자리 a >= b)
        while True:
            a = random.randint(10, 30)
            b = random.randint(1, a - 1)
            if (a % 10) >= (b % 10):
                break
        numbers = [a, b]

    elif difficulty == 4:
        # 특별: 10 배수끼리 빼기 또는 10~18에서 1자리 빼기
        if random.choice([True, False]):
            # 10 배수 뺄셈 (20, 30, ..., 90) - a가 최소 20 이상이어야 b 선택 가능
            tens = [10 * i for i in range(1, 10)]  # 10~90
            a = random.choice(tens[1:])             # 20~90 (10 제외)
            b = random.choice([t for t in tens if t < a])
        else:
            # 10~18에서 1자리 뺄셈 (받아내림 연습)
            # a=19이면 a%10=9라 b 범위가 (10,9)가 되어 오류 → 11~18로 제한
            a = random.randint(11, 18)
            b = random.randint(a % 10 + 1, 9)  # 받아내림이 발생하도록 b > a의 일의 자리
        numbers = [a, b]

    elif difficulty <= 6:
        # 보통: 1~100, 2개 숫자, 받아내림 가능
        a = random.randint(10, 99)
        b = random.randint(1, a - 1)
        numbers = [a, b]

    else:
        # 어려움: 50~100, 3개 숫자 연속 뺄셈
        # a - b - c >= 0 이 되도록 생성
        while True:
            a = random.randint(50, 100)
            b = random.randint(1, a // 2)
            c = random.randint(1, a - b)
            if a - b - c >= 0:
                break
        numbers = [a, b, c]

    return numbers

def create_image(difficulty=5):
    """A4 크기의 뺄셈 문제 이미지 생성 (300 DPI 기준)
    
    Args:
        difficulty: 난이도 (1-10)
    """
    # A4 크기: 210mm x 297mm @ 300 DPI = 2480 x 3508 픽셀
    width, height = 2480, 3508
    
    # 흰색 배경 이미지 생성
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 폰트 설정 (시스템 폰트 사용)
    try:
        title_font = ImageFont.truetype("malgun.ttf", 80)
        header_font = ImageFont.truetype("malgun.ttf", 50)
        problem_font = ImageFont.truetype("arial.ttf", 60)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        problem_font = ImageFont.load_default()
    
    # 헤더 그리기
    title = f"뺄셈 연습 문제 (난이도: {difficulty})"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((width // 2 - title_width // 2, 100), title, fill='black', font=title_font)
    
    # 날짜와 이름란
    name_text = "이름: ________________"
    date_text = "날짜: ____년   ____월   ____일"
    draw.text((width // 4, 220), name_text, fill='black', font=header_font)
    draw.text((width * 3 // 4 - 420, 220), date_text, fill='black', font=header_font)
    
    # 구분선
    draw.line([(200, 320), (width - 200, 320)], fill='black', width=3)
    
    # 36개의 문제 생성
    problems = [generate_subtraction_problem(difficulty) for _ in range(36)]
    
    # 두 열로 나누어 배치
    column_width = (width - 400) // 2  # 좌우 여백 200씩
    start_x_left = 200
    start_x_right = 200 + column_width + 100  # 열 간격 100
    start_y = 420

    # 한 열에 들어갈 최대 행 수
    rows_per_column = 18
    # 하단 여백 (픽셀)
    bottom_margin = 200

    # 문제 행간을 계산해 18행이 A4 내에 들어가도록 조정
    bbox = draw.textbbox((0, 0), "0", font=problem_font)
    line_height = bbox[3] - bbox[1]
    available_space = height - start_y - bottom_margin
    max_spacing = max(10, available_space // (rows_per_column - 1))

    # 폰트 크기 조정
    if hasattr(problem_font, 'size'):
        current_size = problem_font.size
        while line_height + 8 > max_spacing and current_size > 18:
            current_size -= 2
            try:
                problem_font = ImageFont.truetype("arial.ttf", current_size)
            except:
                problem_font = ImageFont.load_default()
                break
            bbox = draw.textbbox((0, 0), "0", font=problem_font)
            line_height = bbox[3] - bbox[1]

    # 최종으로 사용할 문제 간격
    problem_spacing = max_spacing
    
    for i in range(36):
        numbers = problems[i]
        
        # 뺄셈 식 생성
        equation = " - ".join(map(str, numbers)) + " = __________"
        
        # 열 선택 (좌측 18개, 우측 18개)
        if i < 18:
            x = start_x_left
            y = start_y + (i * problem_spacing)
        else:
            x = start_x_right
            y = start_y + ((i - 18) * problem_spacing)
        
        # 문제 식 그리기
        draw.text((x, y), equation, fill='black', font=problem_font)
    
    return img

if __name__ == "__main__":
    # 명령행 인자로 난이도와 개수 받기 (기본값: 난이도=3, 개수=1)
    if len(sys.argv) > 1:
        try:
            difficulty = int(sys.argv[1])
            if difficulty < 1 or difficulty > 10:
                print("⚠ 난이도는 1-10 사이여야 합니다. 기본값(3)을 사용합니다.")
                difficulty = 3
        except ValueError:
            print("⚠ 올바른 숫자를 입력하세요. 기본값(3)을 사용합니다.")
            difficulty = 3
    else:
        difficulty = 3

    # 생성할 이미지 개수 (기본값 1)
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

    print(f"이미지 생성 중... (난이도: {difficulty}, 개수: {count})")

    # output 폴더 생성
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    for i in range(count):
        img = create_image(difficulty)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 인덱스 붙여서 중복 방지
        if count == 1:
            filename = f"subtraction_problems_lv{difficulty}_{timestamp}.png"
        else:
            filename = f"subtraction_problems_lv{difficulty}_{timestamp}_{i+1}.png"

        filepath = os.path.join(output_dir, filename)
        img.save(filepath, 'PNG', dpi=(300, 300))
        saved_files.append(filepath)
        print(f"✓ 뺄셈 문제가 생성되었습니다: {filepath}")

    print(f"✓ 난이도: {difficulty}")
    print(f"✓ 총 {len(saved_files)}개 이미지 생성 완료 (각 이미지에 36문제 포함)")
    print(f"✓ A4 용지에 출력 가능한 이미지 파일입니다.")
    print(f"✓ 큰 수가 왼쪽에 배치되었습니다.")
