import requests
import json
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand

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
    print(f"📡 {filename_prefix} 요청 중...")
    try:
        response = requests.get(api_url, timeout=30)
        
        # 응답 상태 코드 확인
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        # 응답 내용 확인
        print(f"📄 응답 내용: {response.text[:200]}...")  # 처음 200자만 출력
        
        response.raise_for_status()
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {str(e)}")
            print(f"전체 응답 내용: {response.text}")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SAVE_DIR / f"{filename_prefix}_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 저장 완료 → {filename}")
    except requests.exceptions.Timeout:
        print(f"❌ 요청 시간 초과 ({filename_prefix})")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 오류 ({filename_prefix}): {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 실패 ({filename_prefix}): {str(e)}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류 ({filename_prefix}): {str(e)}")

class Command(BaseCommand):
    help = 'OpenAPI에서 보호소와 유기동물 데이터를 JSON으로 저장합니다.'

    def handle(self, *args, **options):
        save_json_from_api(SHELTER_API, "shelter_data")
        save_json_from_api(ANIMAL_API, "animal_data")
        print("🎉 모든 OpenAPI JSON 저장 완료") 