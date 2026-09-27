# 장문수 경력기술서

- 공개 사이트: <https://moonsyu.github.io/career-portpolio/>
- Java 백엔드 회사 업무를 정리한 정적 웹 페이지

## 실행

- 저장소 루트에서 정적 파일 서버 실행 후 브라우저 접속
- 예시: `python -m http.server 8000`
- 접속 주소: <http://localhost:8000>

## 범위

- 원격 백업 관리, 모바일 디지털 지갑 백엔드, 외부 서비스 연동과 조건별 성능 시험
- 직접 제작한 담당 기능 요약과 애플리케이션 흐름도
- 확대 도식의 좌클릭 드래그 이동 · 마우스 휠 확대 및 축소
- 상단 `PDF 다운로드` 버튼으로 경력기술서 파일 저장

## PDF 갱신

- 출력: `output/pdf/Jang-MoonSu-Career.pdf`
- 소개·회사 정보·업무 설명·구현 내용: `index.html`에서 추출
- 도식: 기존 SVG 자산 사용
- 사이트 내용 변경 후 PDF 재생성 및 함께 커밋
- 준비: `python -m pip install -r scripts/requirements-pdf.txt`, `npm install`
- 생성: `python scripts/build_pdf.py`
- 기본 글꼴: Windows 맑은 고딕, PDF에 글꼴 포함
- 다른 환경: `--font-dir`로 `malgun.ttf`와 `malgunbd.ttf`가 있는 폴더 지정
- 공유 Node 패키지 환경: `--node-modules`로 패키지 폴더 지정

## 라이선스

- 본문과 도식: 장문수 경력기술서 용도
- 기술 아이콘: 각 원저작자에게 권리 귀속
- [Devicon 라이선스](assets/architecture/DEVICON-LICENSE.txt)
- [Lucide 라이선스](assets/architecture/LUCIDE-LICENSE.txt)
- [아이콘 출처 목록](assets/architecture/icon-sources.json)
