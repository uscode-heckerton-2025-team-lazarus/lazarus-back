"""
추천 관련 서비스 로직 (Elasticsearch 기반)
"""

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List
import os


class RecommendationService:
    def __init__(self):
        # Initialize Elasticsearch client with environment variable
        es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.es = Elasticsearch([es_url])
        # Initialize sentence transformer model
        self.model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )

    def search_by_category(self, category: str, query_text: str,
                          size: int = 5) -> List[Dict[str, Any]]:
        """
        카테고리별로 검색하는 메서드
        Args:
            category (str): 검색할 카테고리 
                (temple, cultural_heritage, theme_park, tourist_spot, nature, cafe, restraunt)
            query_text (str): 검색할 텍스트
            size (int): 반환할 결과 개수
        Returns:
            List[Dict[str, Any]]: 검색 결과 리스트
        """
        if not query_text or query_text.strip() == "":
            return []
        
        # Convert input text to vector embedding
        text_embedding = self.model.encode(query_text)

        # Prepare search query with category filter
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "script_score": {
                                "query": {"match_all": {}},
                                "script": {
                                    "source": (
                                        "cosineSimilarity(params.query_vector, "
                                        "'content_vector') + 0.1"
                                    ),
                                    "params": {
                                        "query_vector": text_embedding.tolist()
                                    }
                                }
                            }
                        }
                    ],
                    "filter": [
                        {
                            "term": {
                                "category": category
                            }
                        }
                    ]
                }
            },
            "size": size
        }
        
        try:
            response = self.es.search(index="uiseong_attractions_en", body=search_query)
            return [hit['_source'] for hit in response['hits']['hits']]
        except Exception as e:
            if "index_not_found_exception" in str(e):
                return [{"error": "Elasticsearch 인덱스가 존재하지 않습니다. 먼저 데이터를 인덱싱해주세요."}]
            else:
                return [{"error": f"검색 중 오류 발생: {str(e)}"}]

    def search_all_categories(self, extracted_info: Dict[str, str],
                             size: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        추출된 정보를 바탕으로 모든 카테고리에서 검색하는 메서드
        Args:
            extracted_info (Dict[str, str]): Gemini에서 추출한 카테고리별 정보
            size (int): 각 카테고리당 반환할 결과 개수
        Returns:
            Dict[str, List[Dict[str, Any]]]: 카테고리별 검색 결과
        """
        results = {}
        categories = ['temple', 'cultural_heritage', 'theme_park',
                     'tourist_spot', 'nature', 'cafe', 'restraunt']
        
        for category in categories:
            query_text = extracted_info.get(category, "")
            if query_text and query_text.strip() != "":
                category_results = self.search_by_category(
                    category, query_text, size
                )
            else:
                # 추출된 정보가 없으면 빈 리스트 반환
                category_results = []
            
            results[category] = category_results
        
        return results 

    def check_index_structure(self):
        """
        인덱스 구조와 샘플 데이터를 확인하는 메서드
        """
        try:
            # 인덱스 매핑 확인
            mapping = self.es.indices.get_mapping(index="uiseong_attractions_en")
            print("=== 인덱스 매핑 ===")
            print(mapping)
            
            # 샘플 데이터 확인
            sample = self.es.search(
                index="uiseong_attractions_en",
                body={"query": {"match_all": {}}, "size": 1}
            )
            print("\n=== 샘플 데이터 ===")
            print(sample)
            
            # 카테고리별 데이터 수 확인
            categories = ['temple', 'cultural_heritage', 'theme_park', 
                         'tourist_spot', 'nature', 'cafe','restraunt']
            for category in categories:
                count = self.es.count(
                    index="uiseong_attractions_en",
                    body={"query": {"term": {"category": category}}}
                )
                print(f"{category}: {count['count']}개")
                
        except Exception as e:
            print(f"인덱스 확인 중 오류: {str(e)}") 