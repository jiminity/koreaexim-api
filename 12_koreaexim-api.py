# 필요한 모듈 import

import requests
import os
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv

# 필요로 하는 변수, 함수 정의
    # 데이터가 저장될 디렉토리와 파일 이름
load_dotenv()
output_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(output_dir, exist_ok=True)  # 디렉토리 생성

today = datetime.today().strftime("%Y%m%d")
API_KEY = os.getenv("AUTHKEY")
URL = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={API_KEY}&searchdate={today}&data=AP01"

def get_koreaexim():
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
 
    
# dataframe으로 전환한 결과를 csv로 저장
def to_csv(**kwargs): # **kwargs를 사용해서 airflow가 가지고 있는 모든 변수를 건네받습니다.
    print(kwargs)
    ds = kwargs['ds']
    ti = kwargs['ti']
    file_path = os.path.join(output_dir, f'koreaexim-api-{ds}.csv')
    koreaexim_info = get_koreaexim()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # pulled_value = ti.xcom_pull(task_ids='transform_df_task')
    # pulled_value.to_csv(file_path)
    readme_content = f"""README.md 파일을 업데이트 (표 형식 적용)"""

    if not koreaexim_info:
        currency_table = "환율 정보를 가져오는 데 실패했습니다."
    else:
        # 마크다운 표 헤더와 구분선 추가
        currency_table = """| 국가/통화명 | 전신환(송금)받으실때 | 전신환(송금)보내실때 |
|------------|------------------|------------------|
"""
        currency_table += "\n".join(koreaexim_info)

    readme_content = f"""
이 리포지토리는 한국수출입은행 API를 사용하여 환율 정보를 자동으로 업데이트합니다.

## 현재 환율

{currency_table}

:hourglass_flowing_sand: 업데이트 시간: {now} (UTC)

---
자동 업데이트 봇에 의해 관리됩니다.
"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(readme_content)

# DAG 정의
dag = DAG(
    "koreaexim-api",
    default_args={
        'owner': 'fisa',
        'start_date': datetime(2025, 3, 15),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    tags=['koreaexim'],
)


# TASK 정의
get_koreaexim_task = PythonOperator(
    task_id='get_koreaexim_task',
    dag=dag,
    python_callable=get_koreaexim,
    # depends_on_past=True,
    owner="fisa",
    retries=3,
    retry_delay=timedelta(minutes=5),
)

load_csv_task = PythonOperator(
    task_id='load_csv_task',
    dag=dag,
    python_callable=to_csv,
    # depends_on_past=True,
    owner="fisa",
    retries=3,
    retry_delay=timedelta(minutes=5),
)

# TASK 간의 순서를 작성
get_koreaexim_task >> load_csv_task
