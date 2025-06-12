# Pawfect Match 프로젝트

### 팀 데이터노베이스 (소프트웨어학과 202126849 이호영, 소프트웨어학과 202126920 정혁준)

## 설치 및 실행 방법

1. Python 가상환경 생성 및 활성화
```bash
# DB-TEAM 폴더(프로젝트 루트 디렉토리)에서:
python -m venv venv

# 가상환경 활성화
# Windows의 경우:
venv\Scripts\activate
# macOS/Linux의 경우:
source venv/bin/activate
```

2. 필요한 패키지 설치
```bash
# TP 폴더로 이동
cd TP

# 패키지 설치
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

4. 서버 실행
```bash
python manage.py runserver
```

서버가 실행되면 http://127.0.0.1:8000/ 에서 웹사이트에 접속할 수 있습니다.

## 주의사항
- Python 3.8 이상 버전이 필요합니다.
- PostgreSQL 데이터베이스가 설치되어 있어야 합니다.
- 가상환경을 활성화한 상태에서 위의 명령어들을 실행해야 합니다.
- requirements.txt는 TP 폴더 안에 있습니다.
- 프로그램 실행은 TP 폴더 안에서 실행해야 합니다.
- 가상환경(venv)은 프로젝트 루트 디렉토리(DB-TEAM)에 생성하는 것을 권장합니다.
