# Lazarus Backend

관광지 추천 시스템 백엔드 API

## Docker Compose로 배포

### 1. 환경 설정

`.env` 파일을 생성하고 필요한 환경변수를 설정하세요:

```bash
# .env 파일 생성
API_KEY=your_gemini_api_key_here
ELASTICSEARCH_URL=http://elasticsearch:9200
```

### 2. 서비스 실행

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 3. 서비스 접근

- **Backend API**: http://localhost:8000
- **Elasticsearch**: http://localhost:9200
- **API 문서**: http://localhost:8000/docs

### 4. 데이터 인덱싱

Elasticsearch가 준비되면 데이터를 인덱싱해야 합니다:

```bash
# 컨테이너에 접속
docker-compose exec backend python

# Python에서 데이터 인덱싱 스크립트 실행
# (별도 스크립트 필요)
```

### 5. 서비스 상태 확인

```bash
# 서비스 상태 확인
docker-compose ps

# Elasticsearch 헬스체크
curl http://localhost:9200/_cluster/health
```

## 개발 환경

### 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
python main.py
```

### Elasticsearch 로컬 실행

```bash
# Docker로 Elasticsearch 실행
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```