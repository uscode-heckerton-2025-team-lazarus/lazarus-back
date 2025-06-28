from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from datetime import datetime
import numpy as np

# ✅ 모델 로드 (최초 한 번만)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Elasticsearch 연결
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'elastic'),
    verify_certs=False  # 개발 환경에서는 False, 운영 환경에서는 반드시 True
)

# ✅ description을 임베딩하는 함수
def get_embedding_from_description(text: str) -> list:
    embedding = embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

# 의성군 관광지 데이터
UISEONG_ATTRACTIONS =[
  {
    "id": 41,
    "name": "의성마늘보쌈",
    "category": "restaurant",
    "type": "korean",
    "description": "의성의 특산품인 마늘을 활용한 보쌈이 유명한 곳입니다. 신선한 마늘과 함께 먹는 보쌈은 정말 맛있어요. 의성 여행 시 꼭 방문해야 할 맛집입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 42,
    "name": "의성마늘칼국수",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘의 진한 맛이 살아있는 칼국수입니다. 마늘의 매운맛과 칼국수의 고소함이 조화를 이루어 정말 맛있어요. 겨울철에 특히 인기가 많습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 43,
    "name": "의성마늘삼겹살",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘과 함께 구워먹는 삼겹살이 유명한 곳입니다. 마늘의 향과 삼겹살의 고소함이 완벽하게 어우러져서 정말 맛있어요. 가족 모임에 좋은 곳입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 44,
    "name": "의성마늘닭갈비",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 듬뿍 넣어 만드는 닭갈비가 특별합니다. 마늘의 매운맛과 닭고기의 부드러움이 조화를 이루어 정말 맛있어요. 매콤달콤한 양념이 일품입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 45,
    "name": "의성마늘순대",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 순대가 유명한 곳입니다. 마늘의 향이 가득한 순대는 정말 특별한 맛이에요. 의성 여행 시 꼭 맛봐야 할 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 46,
    "name": "의성마늘김치",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 사용해 만드는 김치가 유명한 곳입니다. 마늘의 진한 맛이 살아있는 김치는 정말 맛있어요. 밥반찬으로 최고입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 47,
    "name": "의성마늘된장찌개",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 된장찌개가 특별합니다. 마늘의 향과 된장의 고소함이 조화를 이루어 정말 맛있어요. 건강식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 48,
    "name": "의성마늘국수",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 국수가 유명한 곳입니다. 마늘의 매운맛과 국수의 쫄깃함이 조화를 이루어 정말 맛있어요. 간단한 한끼 식사로 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 49,
    "name": "의성마늘비빔밥",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 비빔밥이 특별합니다. 마늘의 향과 다양한 나물의 맛이 조화를 이루어 정말 맛있어요. 건강식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 50,
    "name": "의성마늘떡볶이",
    "category": "restaurant",
    "type": "korean",
    "description": "의성 마늘을 넣어 만드는 떡볶이가 유명한 곳입니다. 마늘의 매운맛과 떡볶이의 쫄깃함이 조화를 이루어 정말 맛있어요. 간식으로도 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 51,
    "name": "의성마늘피자",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 토핑으로 사용하는 피자가 특별합니다. 마늘의 향과 치즈의 고소함이 조화를 이루어 정말 맛있어요. 이탈리안 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 52,
    "name": "의성마늘파스타",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 넣어 만드는 파스타가 유명한 곳입니다. 마늘의 향과 파스타의 알덴테한 식감이 조화를 이루어 정말 맛있어요. 이탈리안 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 53,
    "name": "의성마늘스테이크",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 소스로 사용하는 스테이크가 특별합니다. 마늘의 향과 스테이크의 부드러움이 조화를 이루어 정말 맛있어요. 고급스러운 분위기입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 54,
    "name": "의성마늘샌드위치",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 넣어 만드는 샌드위치가 유명한 곳입니다. 마늘의 향과 신선한 채소의 맛이 조화를 이루어 정말 맛있어요. 간단한 식사로 좋습니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 55,
    "name": "의성마늘버거",
    "category": "restaurant",
    "type": "western",
    "description": "의성 마늘을 소스로 사용하는 버거가 특별합니다. 마늘의 향과 패티의 고소함이 조화를 이루어 정말 맛있어요. 패스트푸드의 새로운 맛입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 56,
    "name": "의성마늘초밥",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 초밥이 유명한 곳입니다. 마늘의 향과 신선한 생선의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 57,
    "name": "의성마늘라멘",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 라멘이 특별합니다. 마늘의 향과 라멘의 진한 국물이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 58,
    "name": "의성마늘우동",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 우동이 유명한 곳입니다. 마늘의 향과 우동의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 59,
    "name": "의성마늘덮밥",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 덮밥이 특별합니다. 마늘의 향과 다양한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 60,
    "name": "의성마늘탕수육",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 소스로 사용하는 탕수육이 유명한 곳입니다. 마늘의 향과 탕수육의 바삭함이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 61,
    "name": "의성마늘짜장면",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 짜장면이 특별합니다. 마늘의 향과 짜장면의 진한 맛이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 62,
    "name": "의성마늘탕탕이",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 탕탕이가 유명한 곳입니다. 마늘의 향과 탕탕이의 매운맛이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 63,
    "name": "의성마늘깐풍기",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 넣어 만드는 깐풍기가 특별합니다. 마늘의 향과 깐풍기의 바삭함이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 64,
    "name": "의성마늘양꼬치",
    "category": "restaurant",
    "type": "chinese",
    "description": "의성 마늘을 소스로 사용하는 양꼬치가 유명한 곳입니다. 마늘의 향과 양고기의 부드러움이 조화를 이루어 정말 맛있어요. 중국 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 65,
    "name": "의성마늘샤브샤브",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 소스로 사용하는 샤브샤브가 특별합니다. 마늘의 향과 신선한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 66,
    "name": "의성마늘스키야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 스키야키가 유명한 곳입니다. 마늘의 향과 다양한 재료의 맛이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 67,
    "name": "의성마늘오코노미야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 오코노미야키가 특별합니다. 마늘의 향과 오코노미야키의 고소함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 68,
    "name": "의성마늘타코야키",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 타코야키가 유명한 곳입니다. 마늘의 향과 타코야키의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 69,
    "name": "의성마늘오뎅",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 소스로 사용하는 오뎅이 특별합니다. 마늘의 향과 오뎅의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  },
  {
    "id": 70,
    "name": "의성마늘소바",
    "category": "restaurant",
    "type": "japanese",
    "description": "의성 마늘을 넣어 만드는 소바가 유명한 곳입니다. 마늘의 향과 소바의 쫄깃함이 조화를 이루어 정말 맛있어요. 일본 퓨전 음식입니다.",
    "lat": 36.348983,
    "lng": 128.699889
  }
]



# 인덱스 생성
def create_index():
    index_name = "uiseong_attractions_en"
    
    if es.indices.exists(index=index_name):
        print(f"인덱스 '{index_name}'가 이미 존재합니다.")
        return index_name

    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "text", "analyzer": "standard"},
                "category": {"type": "keyword"},
                "type": {"type": "keyword"},
                "lat": {"type": "float"},
                "lng": {"type": "float"},
                "description": {"type": "text", "analyzer": "standard"},
                "content_vector": {
                    "type": "dense_vector",
                    "dims": 384  # MiniLM의 출력 차원
                },
                "created_at": {"type": "date"}
            }
        }
    }

    es.indices.create(index=index_name, body=mapping)
    print(f"✅ 인덱스 '{index_name}' 생성 완료")
    return index_name

# 데이터 업로드
def upload_data(index_name):
    success_count = 0
    error_count = 0

    for attraction in UISEONG_ATTRACTIONS:
        try:
            doc_id = attraction['id']
            embedding = get_embedding_from_description(attraction['description'])

            upload_body = {
                "id": doc_id,
                "name": attraction['name'],
                "category": attraction['category'],
                "type": attraction['category'],
                "lat": float(attraction['lat']) if attraction['lat'] else None,
                "lng": float(attraction['lng']) if attraction['lng'] else None,
                "description": attraction['description'],
                "content_vector": embedding,
                "created_at": datetime.utcnow()
            }

            response = es.index(index=index_name, id=doc_id, body=upload_body)
            if response['result'] in ['created', 'updated']:
                print(f"✅ {attraction['name']} 업로드 성공")
                success_count += 1
            else:
                print(f"❌ {attraction['name']} 업로드 실패")
                error_count += 1

        except Exception as e:
            print(f"❌ {attraction['name']} 업로드 중 오류: {e}")
            error_count += 1

    print(f"\n📊 업로드 결과: 성공 {success_count}개, 실패 {error_count}개")

# 벡터 검색
def vector_search(index_name, query_text, category):
    print(f"\n🔍 벡터 기반 검색 (category = '{category}'):")

    query_vector = get_embedding_from_description(query_text)

    search_query = {
        "query": {
            "bool": {
                "must": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'content_vector') + 0.1",
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                "filter": [
                    {
                        "term": {"category": category}
                    }
                ]
            }
        },
        "size": 5
    }

    response = es.search(index=index_name, body=search_query)
    print(f"검색 결과 {len(response['hits']['hits'])}건:")
    for hit in response["hits"]["hits"]:
        score = hit["_score"]
        source = hit["_source"]
        print(f"  🔹 {source['name']} (score: {score:.4f})")

# 메인 함수
def main():
    print("🚀 Elasticsearch에 의성군 관광지 데이터를 업로드합니다...")

    if not es.ping():
        print("❌ Elasticsearch 연결 실패: 9200 포트 확인 필요")
        return

    print("✅ Elasticsearch 연결 성공")
    index_name = create_index()
    upload_data(index_name)

    test_text = "학문을 닦던 조선시대 서재"
    vector_search(index_name, test_text, category="cultural_heritage")

    print("\n🎉 모든 작업 완료!")

if __name__ == "__main__":
    main()