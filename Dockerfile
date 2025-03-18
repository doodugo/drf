FROM python:3.9-alpine
LABEL maintainer="chlendyd7.com"

WORKDIR /app
EXPOSE 8000

# 시스템 의존성 설치
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .build-deps \
        build-base postgresql-dev musl-dev gcc python3-dev linux-headers && \
    # 가상 환경 생성 후 pip 업그레이드
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip

# requirements.txt 파일을 /tmp로 복사
COPY ./requirements.txt /tmp/requirements.txt

# requirements.txt로 의존성 설치
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apk del .build-deps

# 개발 모드 설정
ARG DEV=false
ENV DEV=${DEV}

# 가상 환경 경로를 PATH에 추가
ENV PATH="/venv/bin:$PATH"

USER root

# 애플리케이션 코드 복사
COPY . .

# Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
