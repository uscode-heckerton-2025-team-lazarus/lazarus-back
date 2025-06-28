#!/bin/bash

# macOS에서 Docker Compose를 사용한 Elasticsearch 7.14.0 실행 스크립트

echo "=== macOS Docker Elasticsearch 7.14.0 실행 시작 ==="

# Docker가 실행 중인지 확인
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되지 않고 있습니다."
    echo "Docker Desktop을 시작해주세요."
    exit 1
fi

echo "✅ Docker가 실행 중입니다."

# 기존 컨테이너가 있다면 중지 및 삭제
echo "기존 컨테이너 정리 중..."
docker-compose down -v 2>/dev/null || true

# Elasticsearch 이미지 다운로드
echo "Elasticsearch 7.14.0 이미지 다운로드 중..."
docker pull elasticsearch:7.14.0

# Kibana 이미지 다운로드
echo "Kibana 7.14.0 이미지 다운로드 중..."
docker pull kibana:7.14.0

# Docker Compose로 서비스 시작
echo "Elasticsearch 및 Kibana 서비스 시작 중..."
docker-compose up -d

# 서비스가 시작될 때까지 대기
echo "서비스 시작 대기 중... (최대 60초)"
sleep 30

# Elasticsearch 상태 확인
echo "Elasticsearch 상태 확인 중..."
if curl -s "http://localhost:9200/_cluster/health?pretty" > /dev/null; then
    echo "✅ Elasticsearch가 성공적으로 시작되었습니다!"
else
    echo "⏳ Elasticsearch가 아직 시작 중입니다. 잠시 더 기다려주세요..."
    sleep 30
    curl -s "http://localhost:9200/_cluster/health?pretty"
fi

echo ""
echo "=== 서비스 정보 ==="
echo "🌐 Elasticsearch: http://localhost:9200"
echo "📊 Kibana: http://localhost:5601"
echo ""
echo "=== 관리 명령어 ==="
echo "📋 로그 확인: docker-compose logs -f"
echo "⏹️  서비스 중지: docker-compose down"
echo "🔄 서비스 재시작: docker-compose restart"
echo "🗑️  완전 삭제: docker-compose down -v"
echo ""
echo "=== 벡터 검색 테스트 ==="
echo "벡터 검색을 테스트하려면 다음 명령어를 실행하세요:"
echo "./mac-vector-test.sh" 