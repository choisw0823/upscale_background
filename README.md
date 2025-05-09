# 이미지 업스케일러 - Real-ESRGAN & BIRNet

최신 AI 모델을 사용하여 이미지 해상도를 향상시키는 Streamlit 기반 웹 애플리케이션입니다. 두 가지 강력한 AI 모델(Real-ESRGAN 및 BIRNet)을 사용하여 낮은 해상도의 이미지를 고품질로 업스케일링할 수 있습니다.

![이미지 업스케일러 데모](https://replicate.delivery/pbxt/6hFTnLlmKEb9VeGm3vBpvISWMBH7FjnvFIyiWLLBCX0x7prQA/output.png)

## 기능

- **Real-ESRGAN** (Replicate)을 사용한 이미지 업스케일링
- **BIRNet** (FAL AI)을 사용한 이미지 품질 향상
- 사용자 친화적인 인터페이스
- 전후 비교를 위한 슬라이더 뷰
- 업스케일된 이미지 다운로드 기능

## 설치 방법

1. 저장소를 클론합니다:
   ```bash
   git clone https://github.com/yourusername/image-upscaler.git
   cd image-upscaler
   ```

2. 가상 환경을 생성하고 활성화합니다:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정:
   `.env` 파일을 생성하고 다음 API 키를 추가합니다:
   ```
   REPLICATE_API_TOKEN=your_replicate_api_token
   FAL_KEY=your_fal_api_key
   ```

## 사용 방법

1. Streamlit 애플리케이션을 실행합니다:
   ```bash
   streamlit run app.py
   ```

2. 웹 브라우저에서 `http://localhost:8501`로 접속합니다.

3. 업스케일링할 이미지를 업로드합니다.

4. 사용할 AI 모델과 필요한 설정을 선택합니다.

5. "이미지 업스케일 시작" 버튼을 클릭합니다.

6. 결과를 확인하고 필요시 업스케일된 이미지를 다운로드합니다.

## API 키 획득 방법

- **Replicate API 키**: [Replicate 웹사이트](https://replicate.com/)에서 계정을 생성하고 API 키를 발급받으세요.
- **FAL API 키**: [FAL AI 웹사이트](https://www.fal.ai/)에서 계정을 생성하고 API 키를 발급받으세요.

## 기술 스택

- [Streamlit](https://streamlit.io/): 웹 인터페이스
- [Replicate](https://replicate.com/): Real-ESRGAN 모델 호스팅
- [FAL AI](https://www.fal.ai/): BIRNet 모델 호스팅
- [PIL/Pillow](https://python-pillow.org/): 이미지 처리
- [Python](https://www.python.org/): 백엔드 로직

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

이슈를 제출하거나 Pull Request를 보내주시면 감사하겠습니다. 모든 기여를 환영합니다! 