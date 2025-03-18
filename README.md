### Docker 설정
Docker가 로컬 환경에 설치되어 있어야 합니다. Docker Compose를 사용하여 애플리케이션을 빌드하고 실행합니다.

#### Docker Compose 명령어:
아래 명령어를 사용하여 Docker 컨테이너를 빌드하고 실행합니다:
```
docker compose up --build
```

### 환경 변수 설정
루트 디렉토리에 `.env` 파일을 생성하고, 아래와 같이 데이터베이스 설정을 추가합니다:

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

값을 실제 데이터베이스 설정에 맞게 변경해 주세요.

### PostgreSQL 데이터베이스
이 프로젝트는 `postgres:16-alpine` 이미지를 사용하는 PostgreSQL을 데이터베이스로 사용합니다. 위의 환경 변수를 바탕으로 PostgreSQL 컨테이너가 설정됩니다.
