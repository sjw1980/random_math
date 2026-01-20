import random
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def generate_addition_problem(difficulty=5):
    """1~100 사이의 숫자로 덧셈 문제 생성 (2개 또는 3개의 숫자)
    
    Args:
        difficulty: 난이도 (1-10)
            1-3: 쉬움 (1-30, 2개 숫자, 일의 자리 합 <= 10)
            4: 특별 (100-149 1개 + 10단위 또는 1단위 1개)
            5-6: 보통 (1-100, 2-3개 숫자)
            7-10: 어려움 (50-100, 3개 숫자)
    """
    if difficulty <= 3:
        # 쉬움 - 일의 자리 합이 10 이하
        num_count = 2
        min_num, max_num = 1, 30
        
        # 일의 자리 합이 10 이하가 될 때까지 반복
        while True:
            numbers = [random.randint(min_num, max_num) for _ in range(num_count)]
            ones_sum = sum(num % 10 for num in numbers)
            if ones_sum <= 10:
                break
    elif difficulty == 4:
        # 특별 - 100~149 1개 + 10단위 또는 1단위 1개
        large_num = random.randint(100, 149)
        
        # 10단위 (10, 20, 30, ..., 90) 또는 1단위 (1~9) 선택
        if random.choice([True, False]):
            # 10단위
            small_num = random.randint(1, 9) * 10
        else:
            # 1단위
            small_num = random.randint(1, 9)
        
        numbers = [large_num, small_num]
    elif difficulty <= 6:
        # 보통
        num_count = random.choice([2, 3])
        min_num, max_num = 1, 100
        numbers = [random.randint(min_num, max_num) for _ in range(num_count)]
    else:
        # 어려움
        num_count = 3
        min_num, max_num = 50, 100
        numbers = [random.randint(min_num, max_num) for _ in range(num_count)]
    
    # 큰 수가 왼쪽에 오도록 정렬 (내림차순)
    numbers.sort(reverse=True)
    
    return numbers

def create_image(difficulty=5):
    """A4 크기의 이미지 생성 (300 DPI 기준)
    
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
    title = f"덧셈 연습 문제 (난이도: {difficulty})"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((width // 2 - title_width // 2, 100), title, fill='black', font=title_font)
    
    # 날짜와 이름란
    date_text = f"날짜: {datetime.now().strftime('%Y년 %m월 %d일')}"
    name_text = "이름: ________________"
    draw.text((width // 4, 220), name_text, fill='black', font=header_font)
    draw.text((width * 3 // 4 - 300, 220), date_text, fill='black', font=header_font)
    
    # 구분선
    draw.line([(200, 320), (width - 200, 320)], fill='black', width=3)
    
    # 30개의 문제 생성
    problems = [generate_addition_problem(difficulty) for _ in range(30)]
    
    # 두 열로 나누어 배치
    column_width = (width - 400) // 2  # 좌우 여백 200씩
    start_x_left = 200
    start_x_right = 200 + column_width + 100  # 열 간격 100
    start_y = 420
    problem_spacing = 190  # 문제 간 간격
    
    for i in range(30):
        numbers = problems[i]
        
        # 큰 수가 왼쪽에 있도록 (이미 정렬되어 있음)
        equation = " + ".join(map(str, numbers)) + " = __________"
        
        # 열 선택 (좌측 15개, 우측 15개)
        if i < 15:
            x = start_x_left
            y = start_y + (i * problem_spacing)
        else:
            x = start_x_right
            y = start_y + ((i - 15) * problem_spacing)
        
        # 문제 식 그리기
        draw.text((x, y), equation, fill='black', font=problem_font)
    
    return img

if __name__ == "__main__":
    # 명령행 인자로 난이도 받기 (기본값: 3)
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
    
    print(f"이미지 생성 중... (난이도: {difficulty})")
    img = create_image(difficulty)
    
    # output 폴더 생성
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # PNG 파일 저장
    filename = f"addition_problems_lv{difficulty}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, 'PNG', dpi=(300, 300))
    
    print(f"✓ 덧셈 문제가 생성되었습니다: {filepath}")
    print(f"✓ 난이도: {difficulty}")
    print(f"✓ 총 30문제 (2열 × 15문제)")
    print(f"✓ A4 용지에 출력 가능한 이미지 파일입니다.")
    print(f"✓ 큰 수가 왼쪽에 배치되었습니다.")
