import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(URL, headers=headers, timeout=10)

load_dotenv()
today = datetime.today().strftime("%Y%m%d")
API_KEY = os.getenv("AUTHKEY")
URL = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={API_KEY}&searchdate={today}&data=AP01"

README_PATH = "README.md"

def get_currency():
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        currency = []
        for cur in data:
            cur_nm = cur["cur_nm"]
            ttb = cur["ttb"]
            tts = cur["tts"]
            currency.append(f"| {cur_nm} | {ttb} | {tts} |")
        return currency
    else:
        return []

def update_readme():
    """README.md 파일을 업데이트 (표 형식 적용)"""
    currency_info = get_currency()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not currency_info:
        currency_table = "환율 정보를 가져오는 데 실패했습니다."
    else:
        # 마크다운 표 헤더와 구분선 추가
        currency_table = """| 국가/통화명 | 전신환(송금)받으실때 | 전신환(송금)보내실때 |
|------------|------------------|------------------|
"""
        currency_table += "\n".join(currency_info)

    readme_content = f"""
이 리포지토리는 한국수출입은행 API를 사용하여 환율 정보를 자동으로 업데이트합니다.

## 현재 환율

{currency_table}

:hourglass_flowing_sand: 업데이트 시간: {now} (UTC)

---
자동 업데이트 봇에 의해 관리됩니다.
"""

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(readme_content)

if __name__ == "__main__":
    update_readme()


