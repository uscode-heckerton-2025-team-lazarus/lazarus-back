#!/bin/bash

# macOS Docker Elasticsearch에서 벡터 유사도 검색 테스트 스크립트

echo "=== macOS Docker Elasticsearch 벡터 검색 테스트 ==="

# Elasticsearch가 실행 중인지 확인
if ! curl -s "http://localhost:9200/_cluster/health?pretty" > /dev/null; then
    echo "❌ Elasticsearch가 실행되지 않고 있습니다."
    echo "먼저 ./mac-elasticsearch.sh를 실행해주세요."
    exit 1
fi

echo "✅ Elasticsearch가 실행 중입니다."

# 벡터 검색을 위한 인덱스 생성
echo "📝 벡터 검색용 인덱스 생성 중..."
curl -X PUT "localhost:9200/vector-index" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      },
      "content_vector": {
        "type": "dense_vector",
        "dims": 768
      }
    }
  }
}'

echo ""

# 샘플 데이터 삽입
echo "📊 샘플 데이터 삽입 중..."
curl -X POST "localhost:9200/vector-index/_doc" -H 'Content-Type: application/json' -d'
{
  "content": "Elasticsearch는 분산형 검색 및 분석 엔진입니다",
  "content_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
}'

curl -X POST "localhost:9200/vector-index/_doc" -H 'Content-Type: application/json' -d'
{
  "content": "머신러닝과 인공지능 기술",
  "content_vector": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]
}'

curl -X POST "localhost:9200/vector-index/_doc" -H 'Content-Type: application/json' -d'
{
  "content": "데이터베이스와 빅데이터 처리",
  "content_vector": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2]
}'

echo ""

# 인덱스 새로고침
echo "🔄 인덱스 새로고침 중..."
curl -X POST "localhost:9200/vector-index/_refresh"

echo ""

# 벡터 유사도 검색 테스트
echo "🔍 벡터 유사도 검색 테스트 중..."
curl -X POST "localhost:9200/vector-index/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "script_score": {
      "query": {
        "match_all": {}
      },
      "script": {
        "source": "cosineSimilarity(params.query_vector, \"content_vector\") + 1.0",
        "params": {
          "query_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        }
      }
    }
  },
  "size": 3
}' | jq '.'

echo ""
echo "=== 테스트 완료 ==="
echo "📊 인덱스 목록 확인: curl -X GET 'localhost:9200/_cat/indices?v'"
echo "🔍 더 많은 검색 테스트는 Kibana에서 가능합니다: http://localhost:5601" 