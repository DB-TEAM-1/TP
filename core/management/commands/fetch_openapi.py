# 파일 위치 예시: scripts/fetch_openapi_json.py

import requests
import json
from datetime import datetime
from pathlib import Path

# ✅ 인코딩된 서비스 키 (꼭 URL 인코딩된 키 사용)
ENCODED_KEY = 'v6SVEDf4sehp1Wz6EBFGg9kVnwecjZnNV%2BXlMlg0rok%2BTc71MmWuwInbylo3t3%2FjCk%2Fl8w3wH8dalIlxdXrBhg%3D%3D'

# ✅ 보호소 정보 API (v2)
SHELTER_API = f'https://apis.data.go.kr/1543061/animalShelterSrvc_v2?serviceKey={ENCODED_KEY}&_type=json&pageNo=1&numOfRows=1000'

# ✅ 유기동물 정보 API
ANIMAL_API = f'https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic?serviceKey={ENCODED_KEY}&_type=json&pageNo=1&numOfRows=1000'

# ✅ JSON 저장 디렉토리
SAVE_DIR = Path("openapi_json")
SAVE_DIR.mkdir(exist_ok=True)

def save_json_from_api(api_url: str, filename_prefix: str):
    print(f" {filename_prefix} 요청 중...")
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SAVE_DIR / f"{filename_prefix}_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f" 저장 완료 → {filename}")
    except Exception as e:
        print(f" 요청 실패 ({filename_prefix}): {e}")

def run():
    save_json_from_api(SHELTER_API, "shelter_data")
    save_json_from_api(ANIMAL_API, "animal_data")
    print("🎉 모든 OpenAPI JSON 저장 완료")
