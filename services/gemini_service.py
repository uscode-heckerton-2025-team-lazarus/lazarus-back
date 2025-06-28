"""
Gemini API를 통한 대화 정보 추출 서비스
"""
from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import Dict

# .env 파일 로드
load_dotenv()


class GeminiService:
    def __init__(self):
        api_key = os.getenv("API_KEY","AIzaSyA0GSV8MsjA362U95b_WmoruGVMliSH9rI")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None

    def extract_travel_info(self, text: str) -> Dict[str, str]:
        """
        대화 내용에서 사찰, 문화재, 테마파크, 관광명소, 자연관광지 정보를 추출하는 메서드
        Args:
            text (str): 대화 내용
        Returns:
            Dict[str, str]: {
                "temple": 내용, "cultural_heritage": 내용, 
                "theme_park": 내용, "tourist_spot": 내용, "nature": 내용
            }
        """
        if not self.gemini_model:
            return {
                "temple": "Gemini API 키가 설정되지 않았습니다.",
                "cultural_heritage": "Gemini API 키가 설정되지 않았습니다.",
                "theme_park": "Gemini API 키가 설정되지 않았습니다.",
                "tourist_spot": "Gemini API 키가 설정되지 않았습니다.",
                "nature": "Gemini API 키가 설정되지 않았습니다.",
                "cafe": "Gemini API 키가 설정되지 않았습니다.",
                "restraunt": "Gemini API 키가 설정되지 않았습니다."
            }
        prompt = (
            "다음 대화 내용에서 사찰, 문화재, 테마파크, 관광명소, 자연관광지,카페,식당에 대한 정보를 추출해주세요.\n"
            "가고 싶지 않은 장소에 대한 내용이 나오면 정보에 대한 결과값에서 제외해주세요.\n"
            "각 카테고리에 해당하는 내용이 없으면 빈 문자열(\"\")로 반환해주세요.\n\n"
            "주의 사항이 있습니다. 사용자의 시간 조정 요청에 스케줄은 동적으로 유연하게 수정되어야 합니다."
            "주의 사항이 있습니다. 사용자의 경로 조정 요청에 경로는 동적으로 유연하게 수정되어야 합니다."
            "주의 사항이 있습니다. 사용자의 일정 추가 요청에 새로운 경로가 적절한 위치에 유연하게 삽입되어야 합니다."
            "주의 사항이 있습니다. 사용자의 일정 제거 요청에 기존 경로가 삭제되고, 사용자가 제거 요청한 관광지가 삭제된 새로운 관광 코스가 도출되어야 합니다."
            f"대화 내용: {text}\n\n"
            "다음 JSON 형태로 응답해주세요:\n"
            "{\n"
            "    \"temple\": \"사찰 관련 내용\",\n"
            "    \"cultural_heritage\": \"문화재 관련 내용\",\n"
            "    \"theme_park\": \"테마파크 관련 내용\",\n"
            "    \"tourist_spot\": \"관광명소 관련 내용\",\n"
            "    \"nature\": \"자연관광지 관련 내용\"\n"
            "    \"cafe\": \"카페 관련 내용\"\n"
            "    \"restraunt\": \"식당 관련 내용\"\n"
            "}"
            
            "다른 추가적인 내용 없이 저 json 형태만 포함해줘"
        )
        try:
            response = self.gemini_model.generate_content(prompt)
            import json
            
            # JSON 부분만 추출 (마크다운 코드 블록 제거)
            text = response.text.strip()
            
            # ```json으로 시작하고 ```로 끝나는 경우 제거
            if text.startswith('```json'):
                text = text[7:]  # ```json 제거
            elif text.startswith('```'):
                text = text[3:]   # ``` 제거
            
            if text.endswith('```'):
                text = text[:-3]  # 끝의 ``` 제거
            
            # JSON 파싱
            result = json.loads(text.strip())
            return result
        except Exception as e:
            return {
                "temple": f"정보 추출 중 오류 발생: {str(e)}",
                "cultural_heritage": f"정보 추출 중 오류 발생: {str(e)}",
                "theme_park": f"정보 추출 중 오류 발생: {str(e)}",
                "tourist_spot": f"정보 추출 중 오류 발생: {str(e)}",
                "nature": f"정보 추출 중 오류 발생: {str(e)}",
                "cafe": f"정보 추출 중 오류 발생: {str(e)}",
                "restraunt": f"정보 추출 중 오류 발생: {str(e)}"
            } 