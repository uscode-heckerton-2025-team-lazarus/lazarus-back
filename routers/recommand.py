"""
    전통주 추천 관련 router
"""

from fastapi import APIRouter, Body
from services.gemini_service import GeminiService
from services.recommendation_service import RecommendationService
from services.tour_planning_service import TourPlanningService

from typing import Dict, List, Any

router = APIRouter()

gemini_service = GeminiService()
recommendation_service = RecommendationService()
tour_planning_service = TourPlanningService()


@router.post("/extract-info")
async def extract_info(text: str = Body(...), size: int = Body(...)):
    """
    대화 내용에서 사찰, 문화재, 테마파크, 관광명소, 자연관광지 정보를 추출하는 엔드포인트
    Args:
        text (str): 대화 내용 전체
    Returns:
        Dict: 추출된 정보와 Elasticsearch 검색 결과
    """

    # Gemini API로 정보 추출
    extracted_info = gemini_service.extract_travel_info(text)
    print(extracted_info)
    # Elasticsearch에서 카테고리별 검색
    search_results = recommendation_service.search_all_categories(
        extracted_info, size
    )
    print(search_results)
    
    return search_results

@router.post("/tour-path")
async def make_tour_path(text: str = Body(...), 
                        locations: Dict[str, List[Dict[str, Any]]] = Body(...), 
                        size: int = Body(...),
                        wake_time: str = Body("07:00"),
                        breakfast_time: str = Body("08:00"),
                        lunch_time: str = Body("12:00"),
                        dinner_time: str = Body("18:00")):
    """
    주어진 위치들을 바탕으로 여행 일정을 생성하는 엔드포인트
    Args:
        text (str): 대화 내용
        locations (Dict[str, List[Dict[str, Any]]]): 카테고리별 위치 정보
        size (int): 여행 일수
        wake_time (str): 기상 시간
        breakfast_time (str): 아침식사 시간
        lunch_time (str): 점심식사 시간
        dinner_time (str): 저녁식사 시간
    Returns:
        List[Dict]: 일별 여행 일정 (위도/경도 정보 포함)
    """
    print("===========")
    print(text)
    print("===========")
    # 여행 일정 생성
    tour_plan = tour_planning_service.make_tour_path(
        locations, text, size, wake_time, breakfast_time, lunch_time, dinner_time
    )
    
    return tour_plan