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


ARCH_BLUE, ARCH_INK, ARCH_LINE = '#2855bf', '#172538', '#b7c8e3'


def component(d, x, y, w, title, icon, lines=(), h=112):
    d.box(x,y,w,h,fill='#f4f7fc',stroke=ARCH_LINE,width=1.8)
    d.icon(icon,x+15,y+15,40,color=ARCH_BLUE)
    d.text(x+66,y+39,title,22,True,anchor='start',fill=ARCH_INK)
    for i,line in enumerate(lines):
        d.text(x+w/2,y+78+i*27,line,20,True,fill='#475467')


def datastore(d, x, y, title, icon, detail):
    d.box(x,y,250,136,fill='#fff',stroke=ARCH_LINE,width=2)
    d.parts.append(f'<ellipse cx="{x+125}" cy="{y+17}" rx="125" ry="17" fill="#f4f7fc" stroke="{ARCH_LINE}" stroke-width="2"/>')
    d.icon(icon,x+22,y+51,43,color=ARCH_BLUE)
    d.text(x+156,y+80,title,24,True,fill=ARCH_INK)
    d.text(x+125,y+115,detail,20,True,fill='#475467')



def web_service(d, x, y, w, h, framework, lines):
    d.box(x,y,w,h,'Web Service',fill='#f7f9fc',stroke='#c9d6e8',width=1.6)
    center=x+w/2
    d.icon('java',center-110,y+75,72)
    d.icon('spring',center+32,y+75,72)
    d.text(center,y+186,framework,23,True)
    for i,line in enumerate(lines):
        d.text(center,y+226+i*31,line,20,fill='#2855bf')


def external_service(d, x, y, w, title, icon, name, lines, h=220):
    d.box(x,y,w,h,title,width=2.6)
    d.node(icon,x+w/2,y+65,name,lines,size=62,color='#2855bf')


def backup():
    d=Diagram('Arabica · 애플리케이션 아키텍처',
        'React·TypeScript 클라이언트와 Spring Boot 웹 서비스, Redis 로그인 토큰 및 JPA·MariaDB 정책·이력 저장소. 애플리케이션 내부 Scheduler가 비동기 Backup Worker를 호출하고 SSH로 원격 Linux에서 정책별 Bash 백업·복원을 실행하는 구조.',900)
    d.box(325,65,975,470,'Application Services · Arabica',width=2.8)
    d.box(20,180,220,300,'Clients',width=2.8)
    d.node('react',130,255,'React · TypeScript','Web Browser',size=80,color=ARCH_BLUE)
    web_service(d,370,145,320,335,'Java · Spring Boot',
        ['Security · JWT 인증','정책 · 스케줄 · 이력 API','JPA Repository'])
    d.node('calendar-clock',835,215,'Scheduler',['예약 작업 호출'],size=74,color=ARCH_BLUE)
    d.node('terminal',1140,215,'Backup Worker',['비동기 실행 · 정책별 명령','Bash · SSH Client'],size=74,color=ARCH_BLUE)
    external_service(d,335,650,270,'Token Store','redis','Redis',['로그인 토큰'])
    external_service(d,645,650,280,'Database','mariadb','MariaDB',['정책 · 실행 이력'])
    d.box(970,650,330,220,'Remote Backup',width=2.6)
    d.icon('linux',1005,712,68)
    d.icon('folder-open',1203,712,62,color=ARCH_BLUE)
    d.text(1040,814,'Linux',22,True)
    d.text(1230,814,'백업 파일',22,True)
    d.text(1135,850,'Bash 백업 · 복원',19,fill='#475467')
    d.arrow([(1085,748),(1190,748)])
    d.arrow([(240,290),(370,290)],'HTTP / JSON',(305,268),both=True)
    d.arrow([(885,252),(1090,252)],'예약 실행',(987,231))
    d.arrow([(470,480),(470,650)],'토큰 저장·조회',(470,568),both=True)
    d.arrow([(630,480),(630,575),(730,575),(730,650)],'JPA / SQL',(680,562),both=True)
    d.arrow([(1090,403),(1090,599),(850,599),(850,650)],'이력 조회·기록',(930,586),both=True)
    d.arrow([(1170,403),(1170,548),(1240,548),(1240,650)],'SSH',(1240,607),both=True)
    return d.save('backup-application.svg')



def backup_async_flow():
    d=Diagram('백업 작업 비동기 분리 흐름','장시간 백업 명령 실행과 파일 전송을 요청 처리와 분리하고, 완료 후 결과 판독·검증·이력 기록으로 연결하는 흐름도.',600)
    d.text(660,58,'백업 작업 비동기 분리 흐름',30,True)
    steps=[('요청 처리','백업 요청 접수'),('비동기 백업 실행','정책별 명령 구성 · SSH 원격 실행'),('결과 연결','판독 · 검증 · 이력 기록')]
    icons=['user-round','file-code','database']
    for i,((title,sub),icon_name) in enumerate(zip(steps,icons)):
        x=105+i*420
        d.box(x,206,290,180,fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
        d.icon(icon_name,x+113,235,64,color='#2855bf')
        d.text(x+145,333,title,23,True)
        d.text(x+145,368,sub,18,fill='#52627b')
        if i<2:d.arrow([(x+292,296),(x+408,296)])
    d.text(660,496,'요청 흐름과 장시간 백업 작업을 분리한 후 결과 확인 흐름으로 연결',21,fill='#52627b')
    return d.save('backup-async-flow.svg')


def wallet_xss_flow():
    d=Diagram('입력값 필터 수정 흐름','기록된 XSS 필터 미적용·처리 오류를 수정하고 후속 최적화로 이어진 3단계 작업 흐름도.',600)
    d.text(660,58,'입력값 필터 수정 흐름',30,True)
    steps=[('문제','XSS 필터 미적용 · 처리 오류'),('조치','XSS 필터 오류 수정'),('후속','XSS 필터 최적화')]
    icons=['file-code','save','package']
    for i,((title,sub),icon_name) in enumerate(zip(steps,icons)):
        x=105+i*420
        d.box(x,206,290,180,fill='#f5f8fd',stroke='#c9d6e8',width=1.5)
        d.icon(icon_name,x+113,235,64,color='#2855bf')
        d.text(x+145,333,title,23,True)
        d.text(x+145,368,sub,18,fill='#52627b')
        if i<2:d.arrow([(x+292,296),(x+408,296)])
    d.text(660,496,'기록된 오류 수정과 최적화 작업의 순서를 정리한 도식',21,fill='#52627b')
    return d.save('wallet-xss-flow.svg')


def wallet():
    d=Diagram('모바일 디지털 지갑 · 애플리케이션 아키텍처',
        '사용자 앱·Dashboard·내부 서버의 요청이 Spring Security 복호화·입력 검증과 Dispatcher를 거쳐 업무 Bean으로 연결되는 프로젝트 구조. 일반 데이터 접근은 MyBatis DAO·Mapper와 PostgreSQL, 알림은 외부 SMS·FCM 서비스를 사용한다.',960)
    d.box(310,70,990,465,'Application Services · Wallet',width=2.8)
    d.box(25,130,215,590,'Clients',width=2.8)
    for y,icon,title in [(190,'smartphone','사용자 앱'),(365,'globe','Dashboard'),(540,'server','내부 서버')]:
        d.node(icon,132,y,title,size=64,color=ARCH_BLUE)
    web_service(d,350,145,330,340,'Java · Spring Boot',
        ['Security · 복호화·입력 검증','Dispatcher · 업무 Bean 선택'])
    d.node('wallet',850,215,'업무 Bean',['회원 · 지갑 · 인증','MyBatis DAO · Mapper'],size=76,color=ARCH_BLUE)
    d.node('bell-ring',1150,215,'알림 모듈',['SMS · FCM 발송 요청'],size=76,color=ARCH_BLUE)
    external_service(d,670,650,320,'Database','postgresql','PostgreSQL',['서비스 데이터'])
    external_service(d,1040,650,260,'Messaging Service','firebase','SMS · FCM',['외부 알림 발송'])
    d.arrow([(240,232),(285,232),(285,275),(350,275)])
    d.arrow([(240,407),(285,407),(285,275)])
    d.arrow([(240,582),(285,582),(285,407)])
    d.text(296,215,'HTTP',18,fill=ARCH_BLUE)
    d.arrow([(680,253),(800,253)])
    d.arrow([(900,253),(1100,253)])
    d.arrow([(850,407),(850,650)],'MyBatis / SQL',(850,592),both=True)
    d.arrow([(1150,381),(1150,650)],'발송 요청',(1150,592))
    d.arrow([(1170,870),(1170,930),(10,930),(10,232),(25,232)],'사용자에게 알림 전달',(610,918))
    return d.save('wallet-application.svg')



def integration():
    d=Diagram('CMP v2.0 · 애플리케이션 아키텍처',
        'React 웹 클라이언트가 Spring WebFlux 서비스에 요청하고, 인증·테넌트 매핑·페이지 처리를 수행하는 서비스가 WebClient로 외부 NSS·NBU API를 연동하는 구조.',900)
    d.box(330,75,970,440,'Application Services · CMP v2.0',width=2.8)
    d.box(20,180,230,300,'Clients',width=2.8)
    d.node('react',135,255,'React', 'Web Browser',size=80,color=ARCH_BLUE)
    web_service(d,380,155,390,320,'Java · Spring WebFlux',
        ['HTTP API · 인증·토큰 관리','테넌트 매핑 · 후속 페이지 처리'])
    d.node('network',1070,215,'WebClient',['외부 API 연동','NSS · NBU'],size=80,color=ARCH_BLUE)
    external_service(d,640,650,300,'External API','server','NSS API',['인증 · Tenant · 백업 정보'])
    external_service(d,990,650,300,'External API','server','NBU API',['cluster · namespace','Job · retention'])
    d.arrow([(250,295),(380,295)],'HTTP / JSON',(315,273),both=True)
    d.arrow([(770,255),(1020,255)],'API 연동',(895,232),both=True)
    d.arrow([(1070,408),(1070,570),(790,570),(790,650)],'NSS API',(875,560),both=True)
    d.arrow([(1100,408),(1100,570),(1140,570),(1140,650)],'NBU API',(1190,600),both=True)
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
    for build in [backup,wallet,integration,backup_restore_verification,integration_response_comparison,integration_tenant_policy,backup_async_flow,wallet_xss_flow]:used |= build()
    print('Built 11 diagrams; icons:', ', '.join(sorted(used)))
