# macOS에서 Docker로 Elasticsearch 7.14.0 실행 가이드

## 개요
- **OS**: macOS (M1/M2/Intel)
- **Elasticsearch 버전**: 7.14.0 (벡터 유사도 검색 지원)
- **방식**: Docker Compose
- **추가 서비스**: Kibana 7.14.0

## 사전 요구사항

### 1. Docker Desktop 설치
```bash
# Homebrew를 통한 설치
brew install --cask docker

# 또는 Docker 공식 사이트에서 다운로드
# https://www.docker.com/products/docker-desktop
```

### 2. Docker 실행 확인
```bash
docker --version
docker-compose --version
```

## 빠른 시작

### 1. 자동화 스크립트 실행 (권장)
```bash
./mac-elasticsearch.sh
```

### 2. 수동 실행
```bash
# Docker Compose로 서비스 시작
docker-compose up -d

# 상태 확인
curl -X GET "localhost:9200/?pretty"
```

## 서비스 정보

### 접근 URL
- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

### 포트
- **Elasticsearch**: 9200 (HTTP), 9300 (Transport)
- **Kibana**: 5601

## 관리 명령어

### 서비스 관리
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f

# 완전 삭제 (데이터 포함)
docker-compose down -v
```

### 컨테이너 관리
```bash
# 실행 중인 컨테이너 확인
docker ps

# 특정 컨테이너 로그 확인
docker logs elasticsearch
docker logs kibana

# 컨테이너 내부 접속
docker exec -it elasticsearch bash
```

## 벡터 유사도 검색 테스트

### 1. 자동화 테스트 스크립트
```bash
./mac-vector-test.sh
```

### 2. 수동 테스트

#### 인덱스 생성
```bash
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
```

#### 데이터 삽입
```bash
curl -X POST "localhost:9200/vector-index/_doc" -H 'Content-Type: application/json' -d'
{
  "content": "Elasticsearch는 분산형 검색 및 분석 엔진입니다",
  "content_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
}'
```

#### 벡터 검색
```bash
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
  }
}'
```

## Kibana 사용

### 1. Kibana 접속
브라우저에서 http://localhost:5601 접속

### 2. Dev Tools 사용
Kibana의 Dev Tools에서 Elasticsearch 쿼리 실행 가능

### 3. 인덱스 패턴 생성
Management > Stack Management > Index Patterns에서 인덱스 패턴 생성

## 문제 해결

### Docker Desktop 메모리 부족
1. Docker Desktop 설정 열기
2. Resources > Memory 설정에서 메모리 증가 (최소 4GB 권장)

### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :9200
lsof -i :5601

# 충돌하는 프로세스 종료
kill -9 <PID>
```

### 컨테이너 시작 실패
```bash
# 로그 확인
docker-compose logs elasticsearch

# 컨테이너 재생성
docker-compose down -v
docker-compose up -d
```

### 데이터 영속성
- 데이터는 Docker 볼륨에 저장됨
- `docker-compose down -v` 실행 시 데이터 삭제됨
- 데이터 백업이 필요한 경우 볼륨 마운트 설정

## 성능 최적화

### 메모리 설정
```yaml
# docker-compose.yml에서
environment:
  - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # 메모리 증가
```

### 디스크 공간
```bash
# 사용하지 않는 Docker 리소스 정리
docker system prune -a
```

## 보안 고려사항

### 개발 환경
- 현재 설정은 개발/테스트용
- 보안 기능 비활성화 (`xpack.security.enabled=false`)

### 프로덕션 환경
- 보안 기능 활성화 필요
- 인증 및 권한 설정
- SSL/TLS 설정
- 방화벽 설정 