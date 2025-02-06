@echo off
REM 저장소 디렉토리로 이동 (자신의 리포지토리 경로로 수정)
cd C:\path\to\your\repo

REM Python 스크립트 실행 (Python이 PATH에 등록되어 있어야 함)
python update_koreaexim.py

REM 변경된 README.md 파일을 Git에 추가하고 커밋 및 푸시
git add README.md
git commit -m "Automated update of currency info: %date% %time%"
git push origin main