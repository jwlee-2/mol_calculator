import streamlit as st
import random

# 페이지 설정 (가장 먼저)
st.set_page_config(
    page_title="몰농도 계산기",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 스타일 + 간단 wave 클래스 (선택사항)
st.markdown("""
<style>
  [data-testid="stSidebar"] { min-width: 380px !important; max-width: 380px !important; }
  /* 출렁이는 액체 효과(미사용 가능) */
  .wave {
    position: relative;
    width: 200px;
    height: 120px;
    overflow: hidden;
  }
  .wave::before {
    content: "";
    position: absolute;
    width: 400%;
    height: 400%;
    background: rgba(0, 119, 255, 0.4);
    border-radius: 40%;
    left: -150%;
    top: 20%;
    animation: wave 6s infinite linear;
  }
  @keyframes wave {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>
""", unsafe_allow_html=True)

st.title("몰농도 계산기")

st.markdown("""
<style>
/* 사이드바 토글 버튼을 왼쪽 상단에 고정 */
[data-testid="collapsedControl"] {
    position: fixed;
    top: 10px;     /* 위에서 10px 정도 떨어뜨리기 */
    left: 0px;     /* 왼쪽 끝 */
    transform: none !important; /* 기본 중앙 정렬 제거 */
    z-index: 1000; /* 다른 요소 위에 표시 */
}
</style>
""", unsafe_allow_html=True)



# ===== 입력값 =====
with st.sidebar:
    st.markdown("<h2 style='margin: 1.5px;'> 몰농도 계산기</h2>", unsafe_allow_html=True)
    st.header("입력값 조정")        # divider 매개변수 제거
    st.divider()                    # 필요 시 별도 구분선

    col_mol1, col_mol2 = st.columns([2, 1])
    with col_mol1:
        target_molarity = st.number_input("원하는 몰농도", min_value=0.0, value=1.0, step=0.01)
    with col_mol2:
        molarity_unit = st.selectbox("단위", options=["M", "mM", "uM"], index=0, key="molarity_unit")

    mw = st.number_input("화학식량/분자량 (g/mol)", min_value=0.1, value=58.44, step=0.01)

    col_vol1, col_vol2 = st.columns([2, 1])
    with col_vol1:
        volume_value = st.number_input("용액의 양", min_value=0.0, value=500.0, step=1.0)
    with col_vol2:
        volume_unit = st.selectbox("단위", options=["mL", "L", "uL"], index=0, key="vol_unit")

# ===== 몰농도 단위 변환 =====
if molarity_unit == "M":
    target_molarity_val = target_molarity
elif molarity_unit == "mM":
    target_molarity_val = target_molarity / 1000
elif molarity_unit == "uM":
    target_molarity_val = target_molarity / 1_000_000
else:
    target_molarity_val = 0.0

# ===== 부피 단위 변환 (리터) =====
if volume_unit == "mL":
    volume_L = volume_value / 1000
elif volume_unit == "L":
    volume_L = volume_value
elif volume_unit == "uL":
    volume_L = volume_value / 1_000_000
else:
    volume_L = 0.0
    
if volume_unit == "mL":
    beaker_width = 150
elif volume_unit == "L":
    beaker_width = 900
elif volume_unit == "uL":
    beaker_width = 50
else:
    beaker_width = 200

# ===== 높이 결정 =====
scaled_height = 400
# 전체 높이를 기준으로 물 높이 (단순히 100*L 로 스케일링)
water_height = min(int(volume_value*1/3), scaled_height)
water_y = scaled_height - water_height

required_mol = target_molarity_val * volume_L
# 필요한 질량 = 필요한 몰수 * 분자량
required_mass = required_mol * mw

particle_rend = []

# 단위 분해 함수
def format_mass(mass):
    units = [
        ("kg", 1000),
        ("g", 1),
        ("mg", 1e-3),
        ("µg", 1e-6)
    ]
    result_parts = []
    remaining = mass

    for unit, factor in units:
        if remaining >= factor:
            value = int(remaining // factor) if factor >= 1 else int((remaining % 1) // factor)
            if factor >= 1:  # 정수 단위 (kg, g)
                value = int(remaining // factor)
                remaining -= value * factor
            else:  # 소수 이하 단위 (mg, µg)
                value = int(round(remaining / factor)) if unit == "µg" else int((remaining // factor) % 1000)
                remaining -= value * factor
            if value > 0:
                result_parts.append(f"{value} {unit}")
                particle_rend.append((value, unit))

    return " ".join(result_parts) if result_parts else "0 g"

# 출력
st.subheader(f"필요한 용질의 질량: {format_mass(required_mass)}")

# ===== 렌더링 =====
wave_threshold = 50  # 물 높이가 이 이상일 때만 출렁임 표시

# 파도 path (윗 경계선만)
if water_height >= wave_threshold:
    # 애니메이션 값들을 미리 계산
    wave_y1 = water_y + 10
    wave_y2 = water_y - 10
    wave_bottom = water_y + 20
    quarter_width = beaker_width // 4
    half_width = beaker_width // 2
    
    # 각 애니메이션 프레임을 미리 생성
    frame1 = f"M0,{water_y} Q{quarter_width},{wave_y1} {half_width},{water_y} T{beaker_width},{water_y} V{wave_bottom} H0 Z"
    frame2 = f"M0,{water_y} Q{quarter_width},{wave_y2} {half_width},{water_y} T{beaker_width},{water_y} V{wave_bottom} H0 Z"
    frame3 = f"M0,{water_y} Q{quarter_width},{wave_y1} {half_width},{water_y} T{beaker_width},{water_y} V{wave_bottom} H0 Z"
    
    wave_path = f'<path d="{frame1}" fill="rgba(0,119,255,0.25)"><animate attributeName="d" dur="4s" repeatCount="indefinite" values="{frame1};{frame2};{frame3}"/></path>'
else:
    wave_path = ""

water_y+5 > water_y + water_height-5
# ===== 입자 SVG 생성 (수정된 부분) =====
MAX_PARTICLES = 100
particles_svg = ""
for i, t in particle_rend:
    count = max(1, min(i, MAX_PARTICLES))  # 최소 1개, 최대 100개
    if t == "kg":
        least_r = 15
    elif t == "g":
        least_r = 6
    elif t == "mg":
        least_r = 2
    elif t == "µg":
        least_r = 1
    else:
        least_r = 1
    
    for _ in range(count):
        cx = random.randint(5, beaker_width-5)
        cy = random.randint(water_y,water_height + water_y)
        r = random.randint(least_r, least_r + 1)
        dur = random.uniform(2, 6)
        delta = random.randint(5, 15)
        
        # 각 애니메이션 값들을 미리 계산
        cy_start = cy
        cy_up = cy - delta
        cy_down = cy + delta
        cy_end = cy
        
        particles_svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="orange"><animate attributeName="cy" values="{cy_start};{cy_up};{cy_down};{cy_end}" dur="{dur}s" repeatCount="indefinite"/></circle>'

# ===== 렌더링 (입자 포함) =====

# if wave_path == "":
    svg_content = f"""
    <div style='position:relative; width:{beaker_width}px; height:{scaled_height}px; margin: 0 auto;'>
        <svg width="{beaker_width}" height="{scaled_height}" viewBox="0 0 {beaker_width} {scaled_height}" xmlns="http://www.w3.org/2000/svg">
            <!-- 비커 외곽선 -->
            <path d="M0,0 L0,{scaled_height} L{beaker_width},{scaled_height} L{beaker_width},0" fill="none" stroke="black" stroke-width="3"/>
            <!-- 물 직사각형 -->    
            <rect x="0" y="{water_y}" width="{beaker_width}" height="{water_height}" fill="rgba(0,119,255,0.25)"/>
            {particles_svg}
        </svg>
    </div>
    """
# else:
    svg_content = f"""
    <div style='position:relative; width:{beaker_width}px; height:{scaled_height}px; margin: 0 auto;'>
        <svg width="{beaker_width}" height="{scaled_height}" viewBox="0 0 {beaker_width} {scaled_height}" xmlns="http://www.w3.org/2000/svg">
            <!-- 비커 외곽선 -->
            <path d="M0,0 L0,{scaled_height} L{beaker_width},{scaled_height} L{beaker_width},0" fill="none" stroke="black" stroke-width="3"/>
            <!-- 물 직사각형 -->
            <rect x="0" y="{water_y}" width="{beaker_width}" height="{water_height}" fill="rgba(0,119,255,0.25)"/>
            {wave_path}
            {particles_svg}
        </svg>
    </div>
    """

st.markdown(svg_content, unsafe_allow_html=True)








