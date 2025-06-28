"""
여행 일정 생성 서비스
"""
from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import Dict, List, Any
import math
import re
import json
from .location_filter_service import LocationFilterService

# .env 파일 로드
load_dotenv()


class TourPlanningService:
    def __init__(self):
        api_key = os.getenv("API_KEY", "AIzaSyA0GSV8MsjA362U95b_WmoruGVMliSH9rI")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        
        # 장소 필터링 서비스 초기화
        self.location_filter = LocationFilterService()

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        두 지점 간의 거리를 계산 (Haversine 공식)
        """
        R = 6371  # 지구의 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def group_locations_by_distance(self, locations: List[Dict[str, Any]], 
                                   locations_per_day: int = 2) -> List[List[Dict[str, Any]]]:
        """
        거리를 기준으로 위치들을 그룹화
        """
        if not locations:
            return []
        
        # 모든 위치를 하나의 리스트로 합치기
        all_locations = []
        for category, locs in locations.items():
            if locs and not (len(locs) == 1 and "error" in locs[0]):
                all_locations.extend(locs)
        
        if not all_locations:
            return []
        
        # 첫 번째 위치부터 시작하여 가장 가까운 위치들을 그룹화
        groups = []
        used_indices = set()
        
        while len(used_indices) < len(all_locations):
            # 아직 사용되지 않은 첫 번째 위치 찾기
            start_idx = None
            for i in range(len(all_locations)):
                if i not in used_indices:
                    start_idx = i
                    break
            
            if start_idx is None:
                break
            
            # 현재 그룹 시작
            current_group = [all_locations[start_idx]]
            used_indices.add(start_idx)
            
            # 가장 가까운 위치들을 찾아서 그룹에 추가
            while len(current_group) < locations_per_day and len(used_indices) < len(all_locations):
                min_distance = float('inf')
                closest_idx = None
                
                for i in range(len(all_locations)):
                    if i in used_indices:
                        continue
                    
                    # 현재 그룹의 모든 위치와의 평균 거리 계산
                    total_distance = 0
                    for loc in current_group:
                        distance = self.calculate_distance(
                            loc['lat'], loc['lng'],
                            all_locations[i]['lat'], all_locations[i]['lng']
                        )
                        total_distance += distance
                    
                    avg_distance = total_distance / len(current_group)
                    if avg_distance < min_distance:
                        min_distance = avg_distance
                        closest_idx = i
                
                if closest_idx is not None:
                    current_group.append(all_locations[closest_idx])
                    used_indices.add(closest_idx)
                else:
                    break
            
            groups.append(current_group)
        
        return groups

    def extract_time_adjustment_request(self, text: str) -> Dict[str, Any]:
        """
        대화 내용에서 시간 조정 요청을 추출
        """
        time_adjustment = {
            "has_request": False,
            "type": None,  # "after", "before", "specific_time", "shift"
            "time": None,
            "shift_hours": None,
            "apply_to": "all",  # "all", "specific_day", "specific_activity"
            "exclude_locations": [],  # 제외할 장소들
            "add_locations": []  # 추가할 장소들
        }
        
        text_lower = text.lower()
        
        # 장소 제외 요청 찾기
        exclude_patterns = [
            r'(.+?)\s*(안가고싶|제외|빼|안가|가지않|싫)',  # "비인 향교는 안가고싶은데 제외해줘"
            r'(.+?)\s*(제외해|빼줘|안가도|가지말)',
            r'(.+?)\s*(는|은)\s*(안가|제외|빼)',
        ]
        
        for pattern in exclude_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                location_name = match[0].strip()
                # 불필요한 단어들 제거
                location_name = re.sub(r'(그|저|이|그런|저런|이런)', '', location_name).strip()
                if location_name and len(location_name) > 1:
                    time_adjustment["exclude_locations"].append(location_name)
                    time_adjustment["has_request"] = True
        
        # 시간 패턴 찾기 (더 포괄적으로)
        time_patterns = [
            r'(\d{1,2})시\s*(이후|후|부터)',  # "2시 이후", "14시 후", "2시부터"
            r'(\d{1,2})시\s*(이전|전|까지)',  # "2시 이전", "14시 전", "2시까지"
            r'(\d{1,2}):(\d{2})\s*(이후|후|부터)',  # "14:30 이후"
            r'(\d{1,2}):(\d{2})\s*(이전|전|까지)',  # "14:30 이전"
            r'모든.*?(\d{1,2})시.*?(이후|이전|후|전|부터|까지)',  # "모든 스케줄을 2시 이후로"
            r'전체.*?(\d{1,2})시.*?(이후|이전|후|전|부터|까지)',  # "전체 일정을 3시 이전으로"
            r'스케줄.*?(\d{1,2})시.*?(이후|이전|후|전|부터|까지)',  # "스케줄이 2시 이후였으면"
            r'일정.*?(\d{1,2})시.*?(이후|이전|후|전|부터|까지)',  # "일정이 3시 이후로"
            r'오후\s*(\d{1,2})시.*?(이후|이전|후|전|부터|까지)',  # "오후 2시 이후"
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                time_adjustment["has_request"] = True
                match = matches[0]
                
                if len(match) == 2:  # 시간만 있는 경우
                    hour = int(match[0])
                    direction = match[1]
                    # 오후 시간 처리
                    if "오후" in text_lower and hour < 12:
                        hour += 12
                elif len(match) == 3:  # 시:분이 있는 경우
                    hour = int(match[0])
                    minute = int(match[1])
                    direction = match[2]
                    time_adjustment["time"] = f"{hour:02d}:{minute:02d}"
                
                if not time_adjustment["time"]:
                    time_adjustment["time"] = f"{hour:02d}:00"
                
                if direction in ["이후", "후", "부터"]:
                    time_adjustment["type"] = "after"
                elif direction in ["이전", "전", "까지"]:
                    time_adjustment["type"] = "before"
                
                break
        
        # 시간 이동 요청 찾기 (예: "1시간 늦춰줘", "30분 앞당겨줘")
        shift_patterns = [
            r'(\d+)시간\s*(늦춰|뒤로|미뤄)',  # "1시간 늦춰줘"
            r'(\d+)시간\s*(앞당겨|앞으로|당겨)',  # "1시간 앞당겨줘"
            r'(\d+)분\s*(늦춰|뒤로|미뤄)',  # "30분 늦춰줘"
            r'(\d+)분\s*(앞당겨|앞으로|당겨)',  # "30분 앞당겨줘"
        ]
        
        for pattern in shift_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                time_adjustment["has_request"] = True
                time_adjustment["type"] = "shift"
                match = matches[0]
                amount = int(match[0])
                direction = match[1]
                
                if "시간" in pattern:
                    time_adjustment["shift_hours"] = amount if direction in ["늦춰", "뒤로", "미뤄"] else -amount
                else:  # 분
                    time_adjustment["shift_hours"] = (amount / 60) if direction in ["늦춰", "뒤로", "미뤄"] else -(amount / 60)
                
                break
        
        return time_adjustment

    def apply_time_adjustment(self, itinerary: List[Dict[str, Any]], adjustment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        시간 조정 요청을 일정에 적용
        """
        if not adjustment["has_request"]:
            return itinerary
        
        adjusted_itinerary = []
        
        for day in itinerary:
            adjusted_day = {
                "day": day["day"],
                "activities": []
            }
            
            for activity in day.get("activities", []):
                # 제외할 장소인지 확인
                should_exclude = False
                activity_location = activity.get("location", "").lower()
                
                for exclude_location in adjustment.get("exclude_locations", []):
                    if exclude_location.lower() in activity_location or activity_location in exclude_location.lower():
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue  # 이 활동은 제외
                
                adjusted_activity = activity.copy()
                
                # 시간 조정 적용
                if adjustment["type"] == "after":
                    # 지정된 시간 이후로 모든 활동 배치
                    target_time = adjustment["time"]
                    current_time = activity.get("time", "09:00")
                    
                    if self._time_to_minutes(current_time) < self._time_to_minutes(target_time):
                        # 시간 간격을 유지하면서 조정
                        time_diff = self._time_to_minutes(target_time) - self._time_to_minutes("09:00")
                        new_minutes = self._time_to_minutes(current_time) + time_diff
                        adjusted_activity["time"] = self._minutes_to_time(new_minutes)
                    else:
                        adjusted_activity["time"] = current_time
                
                elif adjustment["type"] == "before":
                    # 지정된 시간 이전으로 모든 활동 배치
                    target_time = adjustment["time"]
                    current_time = activity.get("time", "09:00")
                    
                    if self._time_to_minutes(current_time) > self._time_to_minutes(target_time):
                        # 이전 시간으로 조정
                        time_diff = self._time_to_minutes(current_time) - self._time_to_minutes(target_time)
                        new_minutes = self._time_to_minutes(current_time) - time_diff - 60
                        new_minutes = max(360, new_minutes)  # 최소 06:00
                        adjusted_activity["time"] = self._minutes_to_time(new_minutes)
                    else:
                        adjusted_activity["time"] = current_time
                    
                elif adjustment["type"] == "shift":
                    # 지정된 시간만큼 이동
                    current_time = activity.get("time", "09:00")
                    current_minutes = self._time_to_minutes(current_time)
                    shift_minutes = int(adjustment["shift_hours"] * 60)
                    new_minutes = current_minutes + shift_minutes
                    
                    # 시간 범위 제한 (06:00 ~ 23:00)
                    new_minutes = max(360, min(1380, new_minutes))  # 06:00 ~ 23:00
                    adjusted_activity["time"] = self._minutes_to_time(new_minutes)
                
                adjusted_day["activities"].append(adjusted_activity)
            
            # 활동이 있는 날만 추가
            if adjusted_day["activities"]:
                adjusted_itinerary.append(adjusted_day)
        
        return adjusted_itinerary

    def _time_to_minutes(self, time_str: str) -> int:
        """시간 문자열을 분으로 변환"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute
        except:
            return 540  # 기본값 09:00

    def _minutes_to_time(self, minutes: int) -> str:
        """분을 시간 문자열로 변환"""
        hour = minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def make_tour_path(self, locations: Dict[str, List[Dict[str, Any]]], 
                      text: str, size: int, 
                      wake_time: str = "07:00",
                      breakfast_time: str = "08:00", 
                      lunch_time: str = "12:00",
                      dinner_time: str = "18:00") -> List[Dict[str, Any]]:
        """
        여행 일정을 생성하는 메서드
        Args:
            locations: 카테고리별 위치 정보
            text: 대화 내용
            size: 여행 일수
            wake_time: 기상 시간
            breakfast_time: 아침식사 시간
            lunch_time: 점심식사 시간
            dinner_time: 저녁식사 시간
        Returns:
            List[Dict]: 일별 여행 일정 (위도/경도 정보 포함)
        """
        if not self.gemini_model:
            return [{"error": "Gemini API 키가 설정되지 않았습니다."}]
        
        # 시간 조정 요청 추출
        time_adjustment = self.extract_time_adjustment_request(text)
        
        # 제외할 장소가 있으면 필터링
        filtered_locations = locations
        if time_adjustment.get("exclude_locations"):
            filtered_locations = self.location_filter.filter_locations_by_exclusion(
                locations, time_adjustment["exclude_locations"]
            )
            print(f"장소 필터링 완료: {time_adjustment['exclude_locations']} 제외")
        
        # 위치들을 거리 기준으로 그룹화
        location_groups = self.group_locations_by_distance(filtered_locations, 2)
        
        # 일수에 맞게 그룹 조정
        if len(location_groups) > size:
            location_groups = location_groups[:size]
        elif len(location_groups) < size:
            # 부족한 일수만큼 빈 그룹 추가
            while len(location_groups) < size:
                location_groups.append([])
        
        # Gemini API로 일정 생성
        prompt = self._create_planning_prompt(location_groups, text, size, 
                                            wake_time, breakfast_time, lunch_time, dinner_time,
                                            time_adjustment)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            
            # JSON 부분만 추출 (마크다운 코드 블록 제거)
            text_response = response.text.strip()
            
            if text_response.startswith('```json'):
                text_response = text_response[7:]
            elif text_response.startswith('```'):
                text_response = text_response[3:]
            
            if text_response.endswith('```'):
                text_response = text_response[:-3]
            
            result = json.loads(text_response.strip())
            
            # 위도/경도 정보 추가
            result = self._add_coordinates_to_itinerary(result, location_groups)
            
            # 시간 조정 적용 (Gemini가 제대로 처리하지 못한 경우를 위한 추가 보정)
            if time_adjustment["has_request"]:
                result = self.apply_time_adjustment(result, time_adjustment)
            
            return result
            
        except Exception as e:
            print(f"Gemini API 오류: {e}")
            # 오류 발생 시 기본 일정 생성
            default_itinerary = self._create_default_itinerary(location_groups, size)
            
            # 시간 조정 적용
            if time_adjustment["has_request"]:
                default_itinerary = self.apply_time_adjustment(default_itinerary, time_adjustment)
            
            return default_itinerary

    def _create_planning_prompt(self, location_groups: List[List[Dict]], 
                               text: str, size: int,
                               wake_time: str = "07:00",
                               breakfast_time: str = "08:00", 
                               lunch_time: str = "12:00",
                               dinner_time: str = "18:00",
                               time_adjustment: Dict[str, Any] = None) -> str:
        """
        Gemini API용 프롬프트 생성
        """
        locations_info = []
        for i, group in enumerate(location_groups):
            day_info = f"Day {i+1}: "
            if group:
                day_info += ", ".join([f"{loc['name']}({loc['description'][:50]}...)" 
                                     for loc in group])
            else:
                day_info += "자유 시간"
            locations_info.append(day_info)
        
        # 시간 조정 요청 정보 추가
        time_adjustment_info = ""
        if time_adjustment and time_adjustment["has_request"]:
            if time_adjustment.get("exclude_locations"):
                exclude_list = ", ".join(time_adjustment["exclude_locations"])
                time_adjustment_info += f"\n\n⚠️ 중요: 사용자가 다음 장소들을 제외해달라고 요청했습니다: {exclude_list}. 이 장소들은 일정에 포함하지 마세요."
            
            if time_adjustment["type"] == "after":
                time_adjustment_info += f"\n\n⚠️ 중요: 사용자가 모든 스케줄을 {time_adjustment['time']} 이후로 배치해달라고 요청했습니다. 모든 활동 시간을 {time_adjustment['time']} 이후로 설정해주세요."
            elif time_adjustment["type"] == "before":
                time_adjustment_info += f"\n\n⚠️ 중요: 사용자가 모든 스케줄을 {time_adjustment['time']} 이전으로 배치해달라고 요청했습니다. 모든 활동 시간을 {time_adjustment['time']} 이전으로 설정해주세요."
            elif time_adjustment["type"] == "shift":
                direction = "늦춰서" if time_adjustment["shift_hours"] > 0 else "앞당겨서"
                hours = abs(time_adjustment["shift_hours"])
                time_adjustment_info += f"\n\n⚠️ 중요: 사용자가 모든 스케줄을 {hours}시간 {direction} 배치해달라고 요청했습니다. 기존 시간에서 해당 시간만큼 조정해주세요."
        
        prompt = f"""
다음 대화 내용과 위치 정보를 바탕으로 {size}일간의 여행 일정을 만들어주세요.

대화 내용: {text}

위치 정보:
{chr(10).join(locations_info)}

각 날짜별로 2개씩 위치가 배정되어 있습니다. 

시간 설정 규칙:
1. 기상 시간: {wake_time}
2. 아침식사 시간: {breakfast_time}
3. 점심식사 시간: {lunch_time}
4. 저녁식사 시간: {dinner_time}
5. 대화 내용에서 언급된 구체적인 시간이 있으면 그 시간을 우선 사용하세요 (예: "아침에", "오후 2시에", "저녁에", "3시", "14:30" 등)
6. 대화 내용에서 시간이 언급되지 않았으면 기본 시간을 사용하세요 (첫 번째 활동: 09:00, 두 번째 활동: 14:00)
7. 대화 내용에서 일정 관련 정보가 있으면 반영하고, 없으면 위치 간 거리와 이동 시간을 고려하여 합리적인 일정을 만들어주세요

"주의 사항이 있습니다. 사용자의 시간 조정 요청에 스케줄은 동적으로 유연하게 수정되어야 합니다."
"주의 사항이 있습니다. 사용자의 경로 조정 요청에 경로는 동적으로 유연하게 수정되어야 합니다."
"주의 사항이 있습니다. 사용자의 일정 추가 요청에 새로운 경로가 적절한 위치에 유연하게 삽입되어야 합니다."
"주의 사항이 있습니다. 사용자의 일정 제거 요청에 기존 경로가 삭제되고, 사용자가 제거 요청한 관광지가 삭제된 새로운 관광 코스가 도출되어야 합니다."

{time_adjustment_info}

다음 JSON 형태로 응답해주세요:
[
    {{
        "day": 1,
        "activities": [
            {{
                "time": "09:00",
                "location": "위치명",
                "description": "활동 설명"
            }},
            {{
                "time": "14:00", 
                "location": "위치명",
                "description": "활동 설명"
            }}
        ]
    }},
    {{
        "day": 2,
        "activities": [
            {{
                "time": "09:00",
                "location": "위치명", 
                "description": "활동 설명"
            }},
            {{
                "time": "14:00",
                "location": "위치명",
                "description": "활동 설명"
            }}
        ]
    }}
]

다른 추가적인 내용 없이 JSON 형태만 포함해주세요.
"""
        return prompt

    def _add_coordinates_to_itinerary(self, itinerary: List[Dict[str, Any]], 
                                     location_groups: List[List[Dict]]) -> List[Dict[str, Any]]:
        """
        일정에 위도/경도 정보를 추가하는 메서드
        """
        # 위치명으로 좌표를 찾기 위한 매핑 생성
        location_map = {}
        for group in location_groups:
            for location in group:
                if 'name' in location and 'lat' in location and 'lng' in location:
                    location_map[location['name']] = {
                        'lat': location['lat'],
                        'lng': location['lng']
                    }
        
        # 일정에 좌표 정보 추가
        for day_plan in itinerary:
            if 'activities' in day_plan:
                for activity in day_plan['activities']:
                    location_name = activity.get('location', '')
                    if location_name in location_map:
                        activity['lat'] = location_map[location_name]['lat']
                        activity['lng'] = location_map[location_name]['lng']
                    else:
                        # 좌표를 찾을 수 없는 경우 기본값 설정
                        activity['lat'] = None
                        activity['lng'] = None
        
        return itinerary

    def _create_default_itinerary(self, location_groups: List[List[Dict]], 
                                 size: int) -> List[Dict[str, Any]]:
        """
        기본 일정 생성 (API 오류 시 사용) - 위도/경도 정보 포함
        """
        itinerary = []
        
        for day in range(1, size + 1):
            day_activities = []
            
            if day <= len(location_groups) and location_groups[day - 1]:
                for i, location in enumerate(location_groups[day - 1]):
                    time = "09:00" if i == 0 else "14:00"
                    activity = {
                        "time": time,
                        "location": location['name'],
                        "description": f"{location['name']} 방문",
                        "lat": location.get('lat'),
                        "lng": location.get('lng')
                    }
                    day_activities.append(activity)
            else:
                # 자유 시간
                day_activities = [
                    {
                        "time": "09:00",
                        "location": "자유 시간",
                        "description": "자유롭게 관광",
                        "lat": None,
                        "lng": None
                    },
                    {
                        "time": "14:00",
                        "location": "자유 시간", 
                        "description": "자유롭게 관광",
                        "lat": None,
                        "lng": None
                    }
                ]
            
            itinerary.append({
                "day": day,
                "activities": day_activities
            })
        
        return itinerary

