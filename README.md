# 장문수 경력기술서

- 공개 사이트: <https://moonsyu.github.io/career-portpolio/>
- Java 백엔드 회사 업무를 정리한 정적 웹 페이지

## 실행

- 저장소 루트에서 정적 파일 서버 실행 후 브라우저 접속
- 예시: `python -m http.server 8000`
- 접속 주소: <http://localhost:8000>

## 범위

- CMP 외부 서비스 연동과 조건별 성능 시험 → Arabica 원격 백업 관리 → 모바일 디지털 지갑 백엔드
- 직접 제작한 담당 기능 요약과 애플리케이션 흐름도
- Arabica: 백업 생성부터 복원 데이터 확인까지 검증 흐름과 MySQL 복원 실험 요약
- CMP: WebFlux 전환 전후 응답시간, 테넌트별 Kubernetes 정책 조회 수정, 운영체제별 부하 비교
- 응답시간 전후 비교와 운영체제별 부하 테스트는 각각의 시험 조건으로 구분
- 확대 도식의 좌클릭 드래그 이동 · 마우스 휠 확대 및 축소
- 상단 `PDF 다운로드` 버튼으로 경력기술서 파일 저장

## CJ올리브네트웍스 DX Engineer 기준 배치

- 기준: [2026년 하반기 공식 JD](https://recruit.cj.net/recruit/ko/recruit/recruit/detail.fo?zz_jo_num=8767), 2026-09-29 재확인
- 해석: Java 시스템 개발·운영과 서비스·데이터 연동에 대한 관련성 순서; 회사가 공개한 프로젝트 선호 순위는 아님
- 보조 참고: [공식 DX Engineer 인터뷰](https://career.cjolivenetworks.co.kr/26f00273-160b-808c-ac55-c16b7c8d1e81)의 외부 인터페이스 운영·개발 사례

| 순서 | 프로젝트 | 배치 이유 |
|---|---|---|
| 1 | CMP | 외부 인증 API 연동, 테넌트별 조회 오류 수정, 조건별 성능 검증을 함께 제시 |
| 2 | Arabica | Java 백엔드에서 정책·일정·원격 실행·로그·복원을 연결한 업무 자동화 경험 |
| 3 | 모바일 디지털 지갑 | 회원·지갑·인증·알림 API 및 입력값 필터 오류 수정 경험 |

## 구현과 트러블슈팅 구분

- CMP: WebFlux 전환을 기존 응답시간 비교 사례로 통합하고 트러블슈팅으로 재분류; 테넌트 조회 카드는 기존 조회 범위 수정 사례에 통합
- Arabica: 장시간 백업 작업의 비동기 분리를 별도 트러블슈팅으로 이동; 운영 장애 발생이나 시간 단축 수치 추가 없음
- 모바일 디지털 지갑: XSS 필터 오류 수정을 별도 트러블슈팅으로 이동; 상세 원인이나 보안 검증 성공률 추정 없음
- 정책·스케줄, 로그 검색·페이징, 회원·지갑 API, 세션·토큰, 알림·문서화 등 일반 기능은 구현 내용에 유지
- CMP 운영체제별 시험: 동일 호스트 사양과 기존 수치 유지; MVC/WebFlux 비교와 별도 시험으로 구분
- Redis 복구와 스케줄 삭제 후 이력 유지 사례는 미사용
- 웹·PDF의 프로젝트 및 상세 사례 순서 동기화

## PDF 갱신

- 출력: `output/pdf/Jang-MoonSu-Career.pdf`
- 소개·회사 정보·업무 설명·구현 내용·개선·트러블슈팅·부하 비교: `index.html`에서 추출
- 도식: 기존 SVG 자산 사용
- 프로젝트별 상세 항목은 `section.detail-page` 순서대로 별도 PDF 페이지 생성
- 사이트 내용 변경 후 PDF 재생성 및 함께 커밋
- 준비: `python -m pip install -r scripts/requirements-pdf.txt`, `npm install`
- 생성: `python scripts/build_pdf.py`
- 기본 글꼴: Windows 맑은 고딕, PDF에 글꼴 포함
- 다른 환경: `--font-dir`로 `malgun.ttf`와 `malgunbd.ttf`가 있는 폴더 지정
- 공유 Node 패키지 환경: `--node-modules`로 패키지 폴더 지정

## 변경 검토 기록 · 2026-09-29

- 웹 360·390·768·900·1280·1500px 화면, 이미지 확대·이동, PDF 다운로드 확인
- PDF 10쪽의 순서·페이지 번호·글자 잘림·겹침 확인
- 기존 링크 ID, 아키텍처, 응답시간 비교 및 부하 비교표 보존 확인
- 독립 검토 결과: 수정 필요 사항 없음
- 아래 모델·추론 수준은 요청 설정이며, 실제 런타임 설정은 도구에서 제공되지 않아 별도 확인 불가

| 에이전트 ID | 요청 설정 | 작업 | 상태 |
|---|---|---|---|
| `/root/three_design_plan` | `gpt-6-astra / xhigh` | JD 대응 순서 및 근거·표현 범위 검토 | 완료 |
| `/root/portfolio_design_ac` | `gpt-5.6-terra / medium` | HTML 구성과 트러블슈팅 도식 수정 | 완료 |
| `/root/design_image_qa` | `gpt-5.6-terra / medium` | 내용·웹·모바일·PDF 독립 검토 | 완료 |

## 라이선스

- 본문과 도식: 장문수 경력기술서 용도
- 기술 아이콘: 각 원저작자에게 권리 귀속
- [Devicon 라이선스](assets/architecture/DEVICON-LICENSE.txt)
- [Lucide 라이선스](assets/architecture/LUCIDE-LICENSE.txt)
- [아이콘 출처 목록](assets/architecture/icon-sources.json)
