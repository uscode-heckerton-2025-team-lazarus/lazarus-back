#!/bin/bash

# Docker를 사용한 Elasticsearch 7.14.0 설치 스크립트

echo "=== Docker Elasticsearch 7.14.0 설치 시작 ==="

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "Docker가 설치되어 있지 않습니다. Docker를 먼저 설치해주세요."
    exit 1
fi

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose가 설치되어 있지 않습니다. Docker Compose를 먼저 설치해주세요."
    exit 1
fi

# Elasticsearch 컨테이너 실행
echo "Elasticsearch 컨테이너 실행 중..."
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "cluster.name=node1" \
  -e "node.name=SingleNode" \
  -e "network.host=0.0.0.0" \
  -e "http.port=9200" \
  -e "cluster.initial_master_nodes=SingleNode" \
  -e "xpack.security.enabled=false" \
  elasticsearch:7.14.0

# 컨테이너가 시작될 때까지 대기
echo "Elasticsearch 시작 대기 중... (최대 60초)"
sleep 30

# Elasticsearch 상태 확인
echo "Elasticsearch 상태 확인 중..."
curl -X GET "localhost:9200/?pretty"

echo "=== Docker Elasticsearch 설치 완료 ==="
echo "Elasticsearch는 http://localhost:9200 에서 접근 가능합니다."
echo ""
echo "컨테이너 관리 명령어:"
echo "  - 중지: docker stop elasticsearch"
echo "  - 시작: docker start elasticsearch"
echo "  - 로그 확인: docker logs elasticsearch"
echo "  - 삭제: docker rm -f elasticsearch" 