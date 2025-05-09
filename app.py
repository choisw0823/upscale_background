import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io
import tempfile
import requests
import replicate
import fal_client
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 확인
if "REPLICATE_API_TOKEN" not in os.environ:
    st.error("REPLICATE_API_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")

if "FAL_KEY" not in os.environ:
    st.error("FAL_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# 페이지 설정을 가장 먼저 호출
st.set_page_config(
    page_title="이미지 처리 도구",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 이미지 비교 컴포넌트 함수 정의
def image_comparison(
    img1, 
    img2, 
    label1="이전", 
    label2="이후", 
    width=900, 
    starting_position=50, 
    show_labels=True
):
    # 이미지를 base64로 인코딩
    def img_to_base64(img):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    img1_b64 = img_to_base64(img1)
    img2_b64 = img_to_base64(img2)
    
    # HTML/JS 코드 생성
    component_id = f"image-compare-{id(img1)}-{id(img2)}"
    component_html = f"""
    <div style="width:{width}px; margin:0 auto; max-width:100%;">
        <div id="{component_id}" class="image-compare" style="width:100%;">
            <div class="image-compare-wrapper">
                <img src="{img1_b64}" alt="{label1}" />
                <div class="image-compare-reveal" style="width:{starting_position}%;">
                    <img src="{img2_b64}" alt="{label2}" />
                    {'<span class="image-compare-label">' + label2 + '</span>' if show_labels else ''}
                </div>
                <div class="image-compare-handle" style="left:{starting_position}%;">
                    <span>&lsaquo; &rsaquo;</span>
                </div>
                {f'<span class="image-compare-label label-left">{label1}</span>' if show_labels else ''}
            </div>
        </div>
    </div>
    
    <style>
        .image-compare {{
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            margin-bottom: 2rem;
        }}
        .image-compare-wrapper {{
            position: relative;
            width: 100%;
            height: 100%;
        }}
        .image-compare-wrapper img {{
            display: block;
            width: 100%;
            height: auto;
        }}
        .image-compare-reveal {{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            overflow: hidden;
        }}
        .image-compare-handle {{
            position: absolute;
            top: 0; 
            bottom: 0;
            width: 4px;
            margin-left: -2px;
            background: rgba(255,255,255,0.95);
            box-shadow: 0 0 12px rgba(0,0,0,0.5);
            cursor: ew-resize;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .image-compare-handle span {{
            color: #333;
            background: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
        }}
        .image-compare-label {{
            position: absolute;
            padding: 8px 16px;
            background: rgba(0,0,0,0.7);
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
            bottom: 15px;
            right: 15px;
        }}
        .label-left {{
            left: 15px;
            right: auto;
        }}
    </style>
    
    <script>
        (function() {{
            const container = document.getElementById('{component_id}');
            if (!container) return;
            
            const wrapper = container.querySelector('.image-compare-wrapper');
            const handle = container.querySelector('.image-compare-handle');
            const reveal = container.querySelector('.image-compare-reveal');
            if (!wrapper || !handle || !reveal) return;
            
            let isDragging = false;
            
            const calculatePosition = (e) => {{
                const rect = wrapper.getBoundingClientRect();
                let position = (e.clientX - rect.left) / rect.width * 100;
                position = Math.max(0, Math.min(100, position));
                return position;
            }};
            
            const move = (position) => {{
                handle.style.left = `${{position}}%`;
                reveal.style.width = `${{position}}%`;
            }};
            
            const startDrag = () => {{
                isDragging = true;
            }};
            
            const endDrag = () => {{
                isDragging = false;
            }};
            
            const drag = (e) => {{
                if (!isDragging) return;
                const position = calculatePosition(e);
                move(position);
            }};
            
            handle.addEventListener('mousedown', startDrag);
            document.addEventListener('mouseup', endDrag);
            document.addEventListener('mousemove', drag);
            
            // 터치 지원
            handle.addEventListener('touchstart', (e) => {{
                startDrag();
                e.preventDefault();
            }}, {{ passive: false }});
            
            document.addEventListener('touchend', endDrag);
            document.addEventListener('touchcancel', endDrag);
            
            document.addEventListener('touchmove', (e) => {{
                if (!isDragging) return;
                const touch = e.touches[0];
                const position = calculatePosition(touch);
                move(position);
                e.preventDefault();
            }}, {{ passive: false }});
        }})();
    </script>
    """
    
    # 컴포넌트 렌더링
    components.html(component_html, height=img1.height, scrolling=False)

# 함수: 이미지 비교 인터페이스
def st_image_comparison(image1, image2, caption1="이전", caption2="이후"):
    """
    Streamlit에서 사용하기 쉬운 이미지 비교 인터페이스
    
    Parameters:
    -----------
    image1 : PIL.Image
        첫 번째 이미지 (왼쪽)
    image2 : PIL.Image
        두 번째 이미지 (오른쪽)
    caption1 : str
        첫 번째 이미지 캡션
    caption2 : str
        두 번째 이미지 캡션
    """
    
    # 두 이미지의 크기 조정
    max_width = 900
    
    if image1.width > max_width:
        # 비율 유지하며 크기 조정
        ratio = max_width / image1.width
        new_height = int(image1.height * ratio)
        image1 = image1.resize((max_width, new_height), Image.LANCZOS)
    
    # 두 번째 이미지를 첫 번째 이미지와 같은 크기로 조정
    image2 = image2.resize(image1.size, Image.LANCZOS)
    
    st.markdown('<div style="text-align:center;"><h4 style="margin-bottom:1.5rem;">슬라이더를 움직여 결과 비교하기</h4></div>', unsafe_allow_html=True)
    
    # 이미지 비교 컴포넌트 표시
    image_comparison(
        img1=image1,
        img2=image2,
        label1=caption1,
        label2=caption2,
        width=max_width,
        starting_position=50,
        show_labels=True
    )

# 함수: Real-ESRGAN으로 이미지 업스케일링
def upscale_with_real_esrgan(image, scale):
    try:
        # 원본 이미지 형식 유지
        img_format = image.format if image.format else "PNG"
        mime_type = f"image/{img_format.lower()}" if img_format else "image/png"
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{img_format.lower() if img_format else 'png'}") as tmp_file:
            image.save(tmp_file, format=img_format if img_format else "PNG")
            temp_image_path = tmp_file.name
        
        # 이미지를 FAL에 업로드하여 URL 얻기
        with open(temp_image_path, "rb") as f:
            img_url = fal_client.upload(f.read(), content_type=mime_type)
        
        # Replicate API 호출
        input = {
            "image": img_url,
            "scale": scale
        }
        
        output = replicate.run(
            "daanelson/real-esrgan-a100:f94d7ed4a1f7e1ffed0d51e4089e4911609d5eeee5e874ef323d2c7562624bed",
            input=input
        )
        
        # 결과 이미지 다운로드
        response = requests.get(output)
        return Image.open(io.BytesIO(response.content))
    
    except Exception as e:
        st.error(f"Real-ESRGAN 처리 중 오류 발생: {str(e)}")
        return None

# 함수: 이미지 배경 제거
def remove_background(image):
    try:
        # 원본 이미지 형식 유지
        img_format = image.format if image.format else "PNG"
        mime_type = f"image/{img_format.lower()}" if img_format else "image/png"
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{img_format.lower() if img_format else 'png'}") as tmp_file:
            image.save(tmp_file, format=img_format if img_format else "PNG")
            temp_image_path = tmp_file.name
        
        # 이미지를 FAL에 업로드하여 URL 얻기
        with open(temp_image_path, "rb") as f:
            img_url = fal_client.upload(f.read(), content_type=mime_type)
        
        # Replicate API 호출 (URL 사용)
        input = {
            "image": img_url
        }
        
        result = replicate.run(
            "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
            input=input
        )
        
        # 결과 이미지 다운로드
        response = requests.get(result)
        return Image.open(io.BytesIO(response.content))
    
    except Exception as e:
        st.error(f"배경 제거 중 오류 발생: {str(e)}")
        return None

# 함수: FAL 클라이언트에 이미지 업로드
def upload_image_to_fal(image):
    try:
        # 원본 이미지 형식 유지
        img_format = image.format if image.format else "PNG"
        mime_type = f"image/{img_format.lower()}" if img_format else "image/png"
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{img_format.lower() if img_format else 'png'}") as tmp_file:
            image.save(tmp_file, format=img_format if img_format else "PNG")
            temp_image_path = tmp_file.name
        
        # FAL에 이미지 업로드
        with open(temp_image_path, "rb") as f:
            url = fal_client.upload(f.read(), content_type=mime_type)
        return url
    
    except Exception as e:
        st.error(f"FAL 업로드 중 오류 발생: {str(e)}")
        return None

# CSS 스타일 적용
st.markdown("""
<style>
    body {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #fff;
    }
    .main {
        background-color: #0e1117;
        color: #fff;
    }
    .stApp {
        max-width: 100%;
        padding: 0;
    }
    h1, h2, h3 {
        color: #fff;
        font-weight: 600;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff2b2b;
    }
    .header {
        margin-bottom: 2rem;
        text-align: center;
    }
    .subheader {
        color: #a0aec0;
        font-size: 1.2rem;
        margin-top: -1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .tab-content {
        background-color: #1e1e24;
        border-radius: 0.5rem;
        padding: 2rem;
        margin-top: 1rem;
    }
    .footer-text {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'scale_factor' not in st.session_state:
    st.session_state['scale_factor'] = 2

# 헤더
st.markdown("<h1 class='header'>이미지 처리 도구</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>업스케일링 또는 배경 제거 중 원하는 기능을 선택하세요</p>", unsafe_allow_html=True)

# 탭 만들기
tab1, tab2 = st.tabs(["🔍 이미지 업스케일링", "✂️ 배경 제거"])

with tab1:
    
    # 업스케일링 비율 선택
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        scale_2x = st.button("2배", type="primary" if st.session_state['scale_factor'] == 2 else "secondary")
        if scale_2x:
            st.session_state['scale_factor'] = 2
            st.rerun()
    
    with col2:
        scale_4x = st.button("4배", type="primary" if st.session_state['scale_factor'] == 4 else "secondary")
        if scale_4x:
            st.session_state['scale_factor'] = 4
            st.rerun()
    
    with col3:
        scale_8x = st.button("8배", type="primary" if st.session_state['scale_factor'] == 8 else "secondary")
        if scale_8x:
            st.session_state['scale_factor'] = 8
            st.rerun()
    
    st.markdown(f"<p style='text-align: center; margin-top: 1rem;'>선택된 배율: <strong>{st.session_state['scale_factor']}x</strong></p>", unsafe_allow_html=True)
    
    # 파일 업로더
    uploaded_file = st.file_uploader("이미지 업로드 (Real-ESRGAN)", type=["jpg", "jpeg", "png", "webp"], key="upscale_file")
    
    # 업로드된 이미지가 있는 경우
    if uploaded_file is not None:
        # 원본 이미지 표시
        original_image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='text-align: center;'>원본 이미지</h4>", unsafe_allow_html=True)
            st.image(original_image, use_container_width=True)
        
        with col2:
            st.markdown("<h4 style='text-align: center;'>업스케일링 결과</h4>", unsafe_allow_html=True)
            
            # 처리 시작 버튼
            process_upscale = st.button("업스케일링 시작", key="start_upscale", use_container_width=True)
            
            # 처리 버튼이 클릭된 경우
            if process_upscale:
                with st.spinner("이미지 업스케일링 중... 잠시만 기다려주세요."):
                    # 이미지 업스케일링 처리
                    result_image = upscale_with_real_esrgan(original_image, st.session_state['scale_factor'])
                
                if result_image:
                    st.success("이미지 업스케일링 완료!")
                    st.image(result_image, use_container_width=True)
                    
                    # 결과 이미지 다운로드 옵션
                    buf = io.BytesIO()
                    result_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="업스케일링된 이미지 다운로드",
                        data=byte_im,
                        file_name=f"upscaled_{st.session_state['scale_factor']}x.png",
                        mime="image/png",
                        use_container_width=True
                    )
            else:
                st.markdown("<div style='text-align: center; padding: 2rem; background-color: #2d2d33; border-radius: 0.5rem;'>업스케일링 결과가 여기에 표시됩니다</div>", unsafe_allow_html=True)
    else:
        # 이미지가 업로드되지 않은 경우 안내 메시지 표시
        st.info("업스케일링을 시작하려면 이미지를 업로드하세요.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    
    # 배경 제거 설명
    st.markdown("<h3 style='margin-bottom: 1rem;'>배경 제거 도구</h3>", unsafe_allow_html=True)
    st.markdown("<p>이미지에서 배경을 자동으로 제거하고 투명한 배경으로 변환합니다.</p>", unsafe_allow_html=True)
    
    # 파일 업로더
    uploaded_file_bg = st.file_uploader("이미지 업로드 (배경 제거)", type=["jpg", "jpeg", "png", "webp"], key="bg_file")
    
    # 업로드된 이미지가 있는 경우
    if uploaded_file_bg is not None:
        # 원본 이미지 표시
        original_image_bg = Image.open(uploaded_file_bg)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='text-align: center;'>원본 이미지</h4>", unsafe_allow_html=True)
            st.image(original_image_bg, use_container_width=True)
        
        with col2:
            st.markdown("<h4 style='text-align: center;'>배경 제거 결과</h4>", unsafe_allow_html=True)
            
            # 처리 시작 버튼
            process_bg = st.button("배경 제거 시작", key="start_bg", use_container_width=True)
            
            # 처리 버튼이 클릭된 경우
            if process_bg:
                with st.spinner("배경 제거 중... 잠시만 기다려주세요."):
                    # 배경 제거 처리
                    result_image = remove_background(original_image_bg)
                
                if result_image:
                    st.success("배경 제거 완료!")
                    # 투명 배경을 보여주기 위한 체커보드 배경 설정
                    st.markdown("""
                    <style>
                    .transparent-bg {
                        background-image: linear-gradient(45deg, #2d2d33 25%, transparent 25%),
                                         linear-gradient(-45deg, #2d2d33 25%, transparent 25%),
                                         linear-gradient(45deg, transparent 75%, #2d2d33 75%),
                                         linear-gradient(-45deg, transparent 75%, #2d2d33 75%);
                        background-size: 20px 20px;
                        background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                        background-color: #3d3d43;
                    }
                    </style>
                    <div class='transparent-bg'>
                    """, unsafe_allow_html=True)
                    st.image(result_image, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 결과 이미지 다운로드 옵션
                    buf = io.BytesIO()
                    result_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="배경이 제거된 이미지 다운로드",
                        data=byte_im,
                        file_name="background_removed.png",
                        mime="image/png",
                        use_container_width=True
                    )
            else:
                st.markdown("<div style='text-align: center; padding: 2rem; background-color: #2d2d33; border-radius: 0.5rem;'>배경 제거 결과가 여기에 표시됩니다</div>", unsafe_allow_html=True)
    else:
        # 이미지가 업로드되지 않은 경우 안내 메시지 표시
        st.info("배경 제거를 시작하려면 이미지를 업로드하세요.")
    
    st.markdown("</div>", unsafe_allow_html=True)

