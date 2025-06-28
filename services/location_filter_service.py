"""
장소 필터링 및 추가 서비스
"""
from typing import Dict, List, Any
import re


class LocationFilterService:
    def __init__(self):
        pass

    def filter_locations_by_exclusion(self, locations: Dict[str, List[Dict[str, Any]]], 
                                     exclude_locations: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        제외할 장소들을 필터링
        """
        if not exclude_locations:
            return locations
        
        filtered_locations = {}
        
        for category, location_list in locations.items():
            filtered_list = []
            
            for location in location_list:
                location_name = location.get('name', '').lower()
                should_exclude = False
                
                for exclude_name in exclude_locations:
                    exclude_name_lower = exclude_name.lower()
                    # 부분 문자열 매칭으로 더 유연하게 처리
                    if (exclude_name_lower in location_name or 
                        location_name in exclude_name_lower or
                        self._similar_names(location_name, exclude_name_lower)):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    filtered_list.append(location)
            
            if filtered_list:  # 빈 리스트가 아닌 경우만 추가
                filtered_locations[category] = filtered_list
        
        return filtered_locations

    def _similar_names(self, name1: str, name2: str) -> bool:
        """
        두 이름이 유사한지 확인 (간단한 유사도 검사)
        """
        # 공백과 특수문자 제거
        clean_name1 = re.sub(r'[^\w가-힣]', '', name1)
        clean_name2 = re.sub(r'[^\w가-힣]', '', name2)
        
        # 길이가 너무 짧으면 정확히 일치해야 함
        if len(clean_name1) <= 2 or len(clean_name2) <= 2:
            return clean_name1 == clean_name2
        
        # 한쪽이 다른 쪽을 포함하는 경우
        if clean_name1 in clean_name2 or clean_name2 in clean_name1:
            return True
        
        # 편집 거리 기반 유사도 (간단한 버전)
        return self._edit_distance(clean_name1, clean_name2) <= 1

    def _edit_distance(self, s1: str, s2: str) -> int:
        """
        간단한 편집 거리 계산
        """
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    def add_nearby_locations(self, locations: Dict[str, List[Dict[str, Any]]], 
                           request_text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        요청에 따라 근처 장소 추가 (향후 확장 가능)
        """
        # 현재는 기본 구현만 제공
        # 실제로는 Elasticsearch나 다른 검색 서비스를 통해 
        # 근처 장소를 찾아서 추가하는 로직이 필요
        return locations

