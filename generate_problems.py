import random
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def generate_addition_problem():
    """1~100 사이의 숫자로 덧셈 문제 생성 (2개 또는 3개의 숫자)"""
    num_count = random.choice([2, 3])  # 2개 또는 3개의 숫자
    numbers = [random.randint(1, 100) for _ in range(num_count)]
    
    # 큰 수가 왼쪽에 오도록 정렬 (내림차순)
    numbers.sort(reverse=True)
    
    return numbers

def create_image():
    """A4 크기의 이미지 생성 (300 DPI 기준)"""
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
    title = "덧셈 연습 문제"
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
    problems = [generate_addition_problem() for _ in range(30)]
    
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
    print("이미지 생성 중...")
    img = create_image()
    
    # output 폴더 생성
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # PNG 파일 저장
    filename = f"addition_problems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, 'PNG', dpi=(300, 300))
    
    print(f"✓ 덧셈 문제가 생성되었습니다: {filepath}")
    print(f"✓ 총 30문제 (2열 × 15문제)")
    print(f"✓ A4 용지에 출력 가능한 이미지 파일입니다.")
    print(f"✓ 큰 수가 왼쪽에 배치되었습니다.")
