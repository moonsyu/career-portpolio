"""Build self-contained, editable application architecture SVGs (Python stdlib)."""
from pathlib import Path
from html import escape
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'architecture'
ICONS = OUT / 'icons'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


class Diagram:
    def __init__(self, title, description, height=800, width=1320):
        self.title, self.description, self.height, self.width = title, description, height, width
        self.parts, self.used = [], set()

    def text(self, x, y, value, size=20, bold=False, anchor='middle', fill='#20252c'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(value)}</text>')

    def box(self, x, y, w, h, title=None, fill='#fff', stroke='#20252c', width=3):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
        if title:
            self.text(x+w/2, y+34, title, 23, True)

    def icon(self, name, x, y, size=64, color='#20252c'):
        self.used.add(name)
        self.parts.append(f'<use href="#icon-{name}" x="{x}" y="{y}" width="{size}" height="{size}" color="{color}"/>')

    def node(self, icon, x, y, title, subtitle=None, size=64, color='#20252c'):
        self.icon(icon, x-size/2, y, size, color)
        self.text(x, y+size+29, title, 22, True)
        if subtitle:
            for i, line in enumerate(subtitle if isinstance(subtitle, list) else [subtitle]):
                self.text(x, y+size+56+25*i, line, 18, fill='#475467')

    def arrow(self, points, label=None, label_xy=None, both=False, dashed=False):
        d='M '+' L '.join(f'{x} {y}' for x,y in points)
        self.parts.append(f'<path d="{d}" fill="none" stroke="#20252c" stroke-width="2.8" stroke-linejoin="round" marker-end="url(#arrow)"'+(' marker-start="url(#arrow-start)"' if both else '')+(' stroke-dasharray="7 6"' if dashed else '')+'/>')
        if label:
            x,y=label_xy
            width=sum(10 if ord(c)<128 else 17 for c in label)+16
            self.parts.append(f'<rect x="{x-width/2}" y="{y-18}" width="{width}" height="25" rx="3" fill="#fff"/>')
            self.text(x,y,label,18)

    def save(self, filename):
        symbols=[]
        for name in sorted(self.used):
            tree=ET.fromstring((ICONS/f'{name}.svg').read_text(encoding='utf-8'))
            view=tree.attrib.get('viewBox','0 0 24 24')
            attrs=' '.join(f'{k}="{escape(v)}"' for k,v in tree.attrib.items() if k not in ['width','height','viewBox','class'] and not k.startswith('{'))
            inner=''.join(ET.tostring(child,encoding='unicode') for child in tree)
            inner=re.sub(r'id="([^"]+)"',lambda m:f'id="{name}-{m[1]}"',inner)
            inner=re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#{name}-{m[1]})',inner)
            symbols.append(f'<symbol id="icon-{name}" viewBox="{view}"><g {attrs}>{inner}</g></symbol>')
        svg=f'''<svg xmlns="{NS}" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(self.title)}</title><desc id="desc">{escape(self.description)}</desc>
<!-- Technology icons: Devicon (MIT); functional icons: Lucide (ISC). See accompanying license files. -->
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#20252c"/></marker><marker id="arrow-start" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M 10 0 L 0 5 L 10 10 Z" fill="#20252c"/></marker>{''.join(symbols)}</defs>
<rect width="{self.width}" height="{self.height}" fill="#fff"/>
<g font-family="Segoe UI, Apple SD Gothic Neo, Malgun Gothic, sans-serif">{''.join(self.parts)}</g></svg>'''
        ET.fromstring(svg)
        (OUT/filename).write_text(svg,encoding='utf-8')
        return self.used



def overview(filename, title, subtitle, items):
    d=Diagram(title, subtitle, 520, 840)
    d.text(46,62,title,32,True,anchor='start')
    d.text(46,101,subtitle,21,anchor='start',fill='#52627b')
    for i,(icon,label,detail) in enumerate(items):
        x=40+i*270
        d.box(x,150,220,282,fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
        d.icon(icon,x+70,190,80,color='#2855bf')
        d.text(x+110,322,label,25,True)
        d.text(x+110,365,detail,20,fill='#52627b')
        d.text(x+22,177,f'0{i+1}',15,True,anchor='start',fill='#2855bf')
    d.text(46,482,'Java · Spring 기반 백엔드 담당 기능',19,anchor='start',fill='#52627b')
    return d.save(filename)


def backup():
    d=Diagram('Arabica · 원격 백업 관리 · 담당 기능 흐름','장문수가 백엔드에서 백업 요청과 일정에 따라 정책별 명령을 구성하고 Apache MINA SSHD와 Bash로 원격 작업을 실행한 담당 기능 중심 설명도.')
    d.text(660,49,'Arabica · 원격 백업 관리 · 담당 기능 흐름',28,True)
    d.node('user-round',103,205,'사용자',['정책 · 일정','실행 · 복원 요청'],size=70)
    d.box(259,99,730,378,'Arabica · Java 17 · Spring Boot 3.2.5')
    d.icon('spring',575,153,52);d.icon('java',645,151,54)
    d.box(288,244,198,184,'정책 · 일정',fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
    d.text(387,325,'전체 · 증분 · 차등',20,True)
    d.text(387,371,'스케줄 관리',21)
    d.box(522,244,198,184,'작업 실행',fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
    d.text(621,325,'명령 구성',21,True)
    d.text(621,371,'비동기 작업 분리',20)
    d.box(756,244,198,184,'결과 관리',fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
    d.text(855,325,'실행 결과 · 검증',20,True)
    d.text(855,371,'로그 · 이력',21)
    d.arrow([(495,340),(513,340)])
    d.arrow([(729,340),(747,340)])
    d.arrow([(149,255),(249,255)],'요청',(199,224))
    d.box(1090,153,208,284,'원격 실행 환경')
    d.node('linux',1194,218,'Linux · Bash','백업 · 복원 실행',size=68)
    d.arrow([(998,285),(1081,285)],'SSH',(1040,255),both=True)
    d.box(332,584,583,158,'작업 이력 · 로그 관리')
    d.node('database',414,639,'',size=48,color='#2855bf')
    d.text(660,666,'검색 · 페이징 · 복원 결과',23,True)
    d.arrow([(620,487),(620,573)],'이력 기록·조회',(620,535),both=True)
    d.text(660,781,'정책 설정 → 원격 작업 → 결과 확인',20,fill='#52627b')
    return d.save('backup-application.svg')


def wallet():
    d=Diagram('모바일 디지털 지갑 · 담당 기능 흐름','웹과 모바일 요청에 대해 로그인·인증, 회원·지갑·거래 API, 데이터 저장, SMS·푸시 알림 기능을 연결하는 일반화된 담당 기능 설명도.')
    d.text(660,49,'모바일 디지털 지갑 · 담당 기능 흐름',28,True)
    d.box(22,163,192,371,'사용자 요청')
    d.node('globe',118,236,'Web',size=57,color='#2855bf')
    d.node('android',118,389,'Mobile',size=57)
    d.box(389,99,535,412,'Java · Spring Boot 백엔드')
    d.icon('java',552,154,61);d.icon('spring',662,154,61)
    d.box(422,255,219,193,'로그인 · 인증',fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
    d.text(531,336,'SSE · QR 로그인',21,True)
    d.text(531,382,'거래 · 스테이킹 인증',19)
    d.box(671,255,219,193,'서비스 API',fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
    d.text(780,336,'회원 · 프로필',21,True)
    d.text(780,382,'지갑 · 연락처',21)
    d.arrow([(224,328),(379,328)],'암호화 통신',(301,292),both=True)
    d.text(301,368,'RSA 기반',20,fill='#52627b')
    d.box(1093,160,202,209,'데이터 저장')
    d.node('database',1194,220,'PostgreSQL',size=63,color='#2855bf')
    d.arrow([(934,269),(1083,269)],'데이터 처리',(1008,237),both=True)
    d.box(442,602,430,145,'알림 기능')
    d.icon('cloud',480,663,50,color='#2855bf')
    d.text(680,697,'SMS · FCM 푸시',25,True)
    d.arrow([(657,521),(657,591)],'알림 처리',(735,561))
    d.arrow([(432,674),(118,674),(118,544)],'사용자에게 알림 전달',(264,648))
    d.text(657,487,'통신 암호화 · 입력값 검증',21,fill='#52627b')
    return d.save('wallet-application.svg')


def integration():
    d=Diagram('CMP · 외부 서비스 연동 · 담당 기능 흐름','외부 인증 API, 세션과 HttpOnly 토큰 처리, 테넌트별 Kubernetes 정책 조회 개선과 조건별 성능 시험을 담당한 기능 설명도.')
    d.text(660,49,'CMP · 외부 서비스 연동 · 담당 기능 흐름',28,True)
    d.node('user-round',105,212,'로그인 요청',size=66)
    d.box(297,116,614,346,'CMP · Java · Spring WebFlux')
    d.icon('spring',407,180,63)
    d.text(653,219,'WebClient · Reactor Mono',25,True)
    d.text(605,288,'외부 인증 API 연동 · 응답 처리',24,True)
    d.text(605,342,'세션 · HttpOnly Cookie 토큰 관리',23)
    d.text(605,401,'Spring MVC → WebFlux 전환',21,fill='#52627b')
    d.arrow([(151,260),(287,260)],'인증 요청',(219,228),both=True)
    d.box(1079,166,218,242,'외부 인증 API')
    d.node('network',1188,229,'인증 응답',size=67,color='#2855bf')
    d.arrow([(921,281),(1069,281)],'API 연동',(995,249),both=True)
    d.box(35,581,354,143,'시험 조건')
    d.text(212,671,'데이터 규모 · 동시 요청',23,True)
    d.box(484,581,345,143,'성능 비교 시험')
    d.text(656,671,'조건별 API 실행 · 관찰',23,True)
    d.box(924,557,373,192,'관찰 지표')
    d.text(1110,642,'응답시간 · P95',23,True)
    d.text(1110,687,'JVM 메모리 · 오류율',23)
    d.arrow([(400,654),(474,654)])
    d.arrow([(839,654),(914,654)])
    return d.save('integration-application.svg')


def backup_restore_verification():
    d=Diagram('백업 복원 검증 흐름','애플리케이션 백업 검증 흐름과 별도의 MySQL·Docker 복원 실험 요약을 구분한 도식.',600)
    d.text(660,52,'백업 파일 생성부터 복원 데이터 확인까지',30,True)
    d.text(52,116,'초기 확인',20,True,anchor='start',fill='#2855bf')
    initial=[('파일 생성','01'),('전송','02'),('로그 저장','03')]
    for i,(title,no) in enumerate(initial):
        x=252+i*276
        d.box(x,92,220,72,fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
        d.text(x+27,120,no,14,True,anchor='start',fill='#2855bf');d.text(x+122,136,title,19,True)
        if i<2:d.arrow([(x+222,128),(x+268,128)])
    d.text(52,232,'개선 후',20,True,anchor='start',fill='#2855bf')
    steps=[('최종 파일·로그','오류 점검'),('DR 전송','대상 준비'),('복원 실행','복원 수행'),('복원 로그·데이터','결과 점검')]
    for i,(title,sub) in enumerate(steps):
        x=222+i*272
        d.box(x,207,228,94,fill='#fff',stroke='#c9d6e8',width=1.5)
        d.text(x+114,245,title,20,True);d.text(x+114,277,sub,18,fill='#52627b')
        if i<3:d.arrow([(x+230,255),(x+264,255)])
    d.box(126,370,1068,164,'MySQL · Docker 복원 실험',fill='#fff',stroke='#2855bf',width=2)
    d.text(340,452,'백업 후 추가',20,True); d.text(340,496,'1행',28,True,fill='#2855bf')
    d.arrow([(460,479),(536,479)])
    d.text(660,452,'전체 복원 후',20,True); d.text(660,496,'추가 데이터 0행',26,True,fill='#2855bf')
    d.arrow([(784,479),(860,479)])
    d.text(980,452,'증분 적용 후',20,True); d.text(980,496,'추가 데이터 1행 복구',24,True,fill='#2855bf')
    return d.save('backup-restore-verification.svg')


def integration_response_comparison():
    d=Diagram('MVC와 WebFlux 응답시간 비교','기록된 평균 응답시간 2,000ms와 584ms를 가로 막대로 비교한 도식. 데이터 건수와 동시 사용자 조건은 기록되지 않았다.',600)
    d.text(660,54,'MVC → WebFlux 평균 응답시간 비교',30,True)
    d.text(660,96,'기록 기준 · 데이터 건수와 동시 사용자 조건 미기재',20,fill='#52627b')
    d.text(177,204,'MVC',23,True,anchor='start')
    d.box(177,229,860,62,fill='#e4e9f1',stroke='#c9d6e8',width=1.5)
    d.parts.append('<rect x="177" y="229" width="860" height="62" rx="20" fill="#52627b"/>')
    d.text(1067,269,'2,000 ms',25,True,anchor='start')
    d.text(177,371,'WebFlux',23,True,anchor='start')
    d.box(177,396,860,62,fill='#e4e9f1',stroke='#c9d6e8',width=1.5)
    d.parts.append('<rect x="177" y="396" width="251" height="62" rx="20" fill="#2855bf"/>')
    d.text(458,436,'584 ms',25,True,anchor='start')
    d.box(424,510,472,58,fill='#f5f8fd',stroke='#acbff0',width=1.5)
    d.text(660,548,'평균 응답시간 70.8% 감소',23,True,fill='#2855bf')
    return d.save('integration-response-comparison.svg')


def integration_tenant_policy():
    d=Diagram('테넌트별 백업 정책 조회 흐름','NSS와 NBU 조회를 분리하고 테넌트, 클러스터, namespace 매핑으로 조회 범위를 조정하는 흐름도.',600)
    d.text(660,52,'테넌트별 백업 정책 조회 범위 조정',30,True)
    d.box(56,210,210,130,'요청 테넌트',fill='#fff',stroke='#c9d6e8',width=1.5)
    d.text(161,286,'정책 조회 요청',20,fill='#52627b')
    d.box(386,116,220,118,'NSS 조회',fill='#fff',stroke='#c9d6e8',width=1.5); d.text(496,191,'정책 조회',20,fill='#52627b')
    d.box(386,314,220,118,'NBU 조회',fill='#fff',stroke='#c9d6e8',width=1.5); d.text(496,389,'정책 조회',20,fill='#52627b')
    d.box(736,210,252,130,'매핑 필터',fill='#f5f8fd',stroke='#acbff0',width=1.5)
    d.text(862,282,'테넌트 · 클러스터',20,True); d.text(862,313,'namespace',20,True)
    d.box(1084,210,190,130,'정책 목록',fill='#f5f8fd',stroke='#acbff0',width=1.5)
    d.text(1179,286,'해당 테넌트',20,True); d.text(1179,317,'결과',20,True)
    d.arrow([(268,275),(333,275),(333,175),(376,175)])
    d.arrow([(268,275),(333,275),(333,373),(376,373)])
    d.arrow([(608,175),(680,175),(680,255),(726,255)])
    d.arrow([(608,373),(680,373),(680,295),(726,295)])
    d.arrow([(990,275),(1074,275)])
    d.text(660,485,'NSS · NBU 조회 분리 → 매핑 필터 합류 → 해당 테넌트 정책 목록',22,True)
    d.text(660,548,'페이지 처리 · API 로그는 조회 흐름 점검의 보조 기록',20,fill='#52627b')
    return d.save('integration-tenant-policy.svg')


if __name__ == '__main__':
    used=set()
    used |= overview('backup-overview.svg','Arabica · 원격 백업 관리','정책 · 실행 · 결과를 연결하는 백엔드',[('file-code','백업 정책','전체 · 증분 · 차등'),('linux','원격 실행','SSH · Bash'),('database','이력 · 복원','검증 · 검색 · 보관')])
    used |= overview('wallet-overview.svg','모바일 디지털 지갑','인증 · 데이터 보호 · 알림 기능 개발',[('user-round','회원 · 지갑','서비스 API'),('network','인증 · 보안','SSE · QR · RSA'),('cloud','알림','SMS · FCM')])
    used |= overview('integration-overview.svg','CMP · 외부 서비스 연동','인증 API 연동과 조건별 성능 비교',[('spring','WebFlux','구조 전환'),('network','인증 연동','WebClient 공통화'),('server','성능 시험','응답 · 메모리 · 오류')])
    for build in [backup,wallet,integration,backup_restore_verification,integration_response_comparison,integration_tenant_policy]:used |= build()
    print('Built 9 diagrams; icons:', ', '.join(sorted(used)))
