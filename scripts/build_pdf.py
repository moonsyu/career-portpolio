"""Build the downloadable career PDF from index.html and its existing assets.

Dependencies: Python reportlab/Pillow and Node sharp. Fonts are embedded.
"""
from argparse import ArgumentParser
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import os
import subprocess
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output/pdf/Jang-MoonSu-Career.pdf'
INK, BLUE, MUTED, LINE, PAPER = map(colors.HexColor,
    ['#172538', '#2355de', '#47556b', '#dce3ed', '#f4f7fc'])
W, H = A4
M, CW = 38, W - 76


class Element:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def select(self, tag=None, cls=None, id=None):
        result = []
        for child in self.children:
            if isinstance(child, Element):
                if ((not tag or child.tag == tag) and
                    (not cls or cls in child.attrs.get('class', '').split()) and
                    (not id or child.attrs.get('id') == id)):
                    result.append(child)
                result.extend(child.select(tag, cls, id))
        return result

    def one(self, **kwargs):
        found = self.select(**kwargs)
        if len(found) != 1:
            raise ValueError(f'Expected one element: {kwargs}, got {len(found)}')
        return found[0]

    def text(self):
        return ' '.join(''.join(c.text() if isinstance(c, Element) else c
                                for c in self.children).split()).replace('—', '-')


class Document(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, source):
        super().__init__()
        self.root = Element()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.stack[-1].children.append(' · ')
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if tag not in self.VOID:
            if self.stack[-1].tag != tag:
                raise ValueError(f'Unbalanced HTML at {tag}')
            self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def build(font_dir, node_modules=None):
    for name, filename in [('Career', 'malgun.ttf'), ('CareerBold', 'malgunbd.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    doc = Document((ROOT / 'index.html').read_text(encoding='utf-8')).root
    projects = doc.select(tag='article', cls='project')
    page_count = 1 + sum(1 + len(p.select(cls='detail-page')) for p in projects)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1, invariant=1)
    pdf.setTitle('장문수 | 경력기술서')
    pdf.setAuthor('Jang MoonSu')
    pdf.setSubject('Java 백엔드 회사 업무')

    def text(value, x, top, width=CW, size=11, bold=False, color=INK, leading=None, max_bottom=H-35):
        style = ParagraphStyle('career', fontName='CareerBold' if bold else 'Career',
            fontSize=size, leading=leading or size * 1.55, textColor=color,
            wordWrap='CJK', splitLongWords=True)
        p = Paragraph(escape(value), style)
        _, height = p.wrap(width, H)
        if top + height > max_bottom:
            raise ValueError(f'PDF page overflow: {value}')
        p.drawOn(pdf, x, H - top - height)
        return top + height

    def rule(top):
        pdf.setStrokeColor(LINE)
        pdf.line(M, H - top, W - M, H - top)

    def footer(page):
        rule(H - 35)
        text('Jang MoonSu · CAREER', M, H - 29, size=8, color=MUTED, max_bottom=H-8)
        text(f'{page:02d} / {page_count:02d}', W - 90, H - 29, 52, 8, color=MUTED, max_bottom=H-8)
        pdf.showPage()

    def picture(path, x, top, width, height):
        pdf.drawImage(ImageReader(str(path)), x, H - top - height, width, height,
                      preserveAspectRatio=True, anchor='c', mask='auto')

    with tempfile.TemporaryDirectory(prefix='career-pdf-') as temp:
        temp = Path(temp)
        images = {}
        jobs = []
        for project in projects:
            for cls in ['work-visual', 'application-architecture']:
                source = project.one(cls=cls).one(tag='img').attrs['src']
                original = ROOT / source
                dest = temp / (original.stem + '.png')
                jobs.append({'source': str(original), 'dest': str(dest)})
                images[(project.attrs['id'], cls)] = dest
            for section in project.select(cls='detail-page'):
                for img in section.select(tag='img'):
                    original = ROOT / img.attrs['src']
                    if original.suffix.lower() == '.svg':
                        dest = temp / (original.stem + '.png')
                        jobs.append({'source': str(original), 'dest': str(dest)})
                    else:
                        dest = original
                    images[img.attrs['src']] = dest
        manifest = temp / 'images.json'
        manifest.write_text(json.dumps(jobs), encoding='utf-8')
        env = os.environ.copy()
        if node_modules:
            env['NODE_PATH'] = str(node_modules)
        # SVG rasterization is an asset build, with no browser or network access.
        subprocess.run(['node', '-e', """
const sharp = require('sharp');
const fs = require('node:fs');
const jobs = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
(async () => { for (const j of jobs) {
  await sharp(j.source, { density: 192 }).png().toFile(j.dest);
} })().catch(e => { console.error(e); process.exitCode = 1; });
""", str(manifest)], check=True, env=env, cwd=ROOT)

        text('JANG MOONSU / CAREER PROFILE', M, 38, size=10, bold=True, color=BLUE)
        text('Java 백엔드', M, 70, size=28, bold=True)
        text('경력기술서', M, 111, size=32, bold=True, color=BLUE)
        text(doc.one(cls='hero-description').text(), M, 173, size=12, bold=True)
        rule(221)
        profile = doc.one(cls='profile-heading')
        picture(ROOT / profile.one(tag='img').attrs['src'], M, 246, 76, 92)
        text(profile.one(tag='h3').text(), M + 94, 251, size=21, bold=True)
        text(profile.one(tag='p').text(), M + 94, 290, size=11, bold=True, color=BLUE)
        y = 360
        for row in doc.one(cls='career-facts').children:
            if isinstance(row, Element):
                text(row.one(tag='dt').text(), M, y, 70, 10, color=MUTED)
                text(row.one(tag='dd').text(), M + 80, y, CW - 80, 12, bold=True)
                y += 29
        text('담당 업무', M, 501, size=15, bold=True)
        gap = 13
        tile = (CW - gap * (len(projects) - 1)) / len(projects)
        for i, project in enumerate(projects):
            x = M + (tile + gap) * i
            picture(images[(project.attrs['id'], 'work-visual')], x, 538, tile, tile * 520 / 840)
            title = project.one(tag='h3').text().split(' · ', 1)
            bottom = text(f'0{i+1}  ' + title[0], x, 652, tile, 11, bold=True)
            if len(title) > 1:
                text(title[1], x, bottom+5, tile, 10, bold=True, color=MUTED)
        text(doc.one(cls='about-copy').text(), M, 714, size=11, bold=True)
        email = doc.one(cls='contact-links').select(tag='a')[0].attrs['href']
        site = next(link.attrs['href'] for link in doc.select(tag='link')
                    if link.attrs.get('rel') == 'canonical')
        text(email.replace('mailto:', ''), M, 764, size=9, color=BLUE)
        pdf.linkURL(email, (M, H-785, M+200, H-760), relative=0)
        text('moonsyu.github.io/career-portpolio', M+220, 764, CW-220, 9, color=BLUE)
        pdf.linkURL(site, (M+220, H-785, W-M, H-760), relative=0)
        footer(1)

        page_number = 2
        for number, project in enumerate(projects, 1):
            text(f'0{number} / WORK', M, 32, size=9, bold=True, color=BLUE)
            text(project.one(tag='h3').text(), M, 52, size=23, bold=True)
            desc = project.one(cls='project-description')
            text(desc.one(cls='project-meta').text(), M, 96, size=9, color=MUTED)
            y = text(desc.one(tag='h4').text(), M, 118, size=12, bold=True)
            y += 9
            for item in desc.select(tag='ul')[0].select(tag='li'):
                y = text('• ' + item.text(), M, y, size=10.5, bold=True, leading=16) + 5
            y = text(desc.one(cls='techline').text(), M, y+2, size=9, color=BLUE) + 12
            rule(y)
            y += 12
            text('APPLICATION ARCHITECTURE', M, y, size=9, bold=True, color=BLUE)
            image_top = y + 20
            picture(images[(project.attrs['id'], 'application-architecture')],
                    M, image_top, CW, CW * 800 / 1320)
            y = image_top + CW * 800 / 1320 + 12
            text('IMPLEMENTATION', M, y, size=9, bold=True, color=BLUE)
            y += 23
            cards = [c for c in project.one(cls='work-detail-list').children if isinstance(c, Element)]
            width = (CW - 20 * (len(cards)-1)) / len(cards)
            for i, card in enumerate(cards):
                x = M + (width+20)*i
                cy = text(card.one(tag='h5').text(), x, y, width, 11, bold=True, color=BLUE) + 6
                for item in card.select(tag='li'):
                    cy = text('• ' + item.text(), x, cy, width, 10, bold=True, leading=15) + 5
            footer(page_number)
            page_number += 1

            # Every project detail is read from the website, in document order.
            # Benchmarks retain their own conditions instead of borrowing those
            # of the separate MVC/WebFlux response-time comparison.
            for section in project.select(cls='detail-page'):
                kind = section.attrs.get('data-page-kind', 'improvement')
                label = {'improvement': 'IMPROVEMENT',
                         'troubleshooting': 'TROUBLESHOOTING',
                         'benchmark': 'PERFORMANCE TEST'}[kind]
                text(f'0{number} / {label}', M, 32, size=9, bold=True, color=BLUE)
                y = text(project.one(tag='h3').text(), M, 52, size=23, bold=True) + 12
                y = text(section.one(cls='detail-title').text(), M, y,
                         size=16, bold=True) + 18
                rule(y)
                y += 18

                facts = section.select(cls='case-facts')
                if facts:
                    rows = [c for c in facts[0].children if isinstance(c, Element)]
                    column = (CW - 28) / len(rows)
                    bottoms = []
                    for i, row in enumerate(rows):
                        x = M + (column + 14) * i
                        cy = text(row.one(tag='dt').text(), x, y, column,
                                  11, bold=True, color=BLUE) + 7
                        dd = row.one(tag='dd')
                        items = dd.select(tag='li')
                        for value in ([item.text() for item in items] or [dd.text()]):
                            cy = text('• ' + value, x, cy, column, 10.5,
                                      bold=True, leading=16) + 6
                        bottoms.append(cy)
                    y = max(bottoms) + 16

                contexts = section.select(cls='benchmark-context')
                for context in contexts:
                    for item in context.select(tag='li'):
                        y = text('• ' + item.text(), M, y, size=11,
                                 bold=True, leading=17) + 6
                    y += 14

                for table in section.select(cls='benchmark-table'):
                    captions = table.select(tag='caption')
                    if captions:
                        y = text(captions[0].text(), M, y, size=12,
                                 bold=True, color=BLUE) + 12
                    rows = table.select(tag='tr')
                    for row_index, row in enumerate(rows):
                        cells = [c for c in row.children if isinstance(c, Element)]
                        width = CW / len(cells)
                        row_height = 43
                        if y + row_height > H - 45:
                            raise ValueError('Benchmark table exceeds PDF page')
                        pdf.setFillColor(BLUE if row_index == 0 else
                                         PAPER if row_index % 2 else colors.white)
                        pdf.rect(M, H-y-row_height, CW, row_height, fill=1, stroke=0)
                        for i, cell in enumerate(cells):
                            text(cell.text(), M+i*width+10, y+10, width-20,
                                 10.5, bold=True,
                                 color=colors.white if row_index == 0 else INK,
                                 max_bottom=y+row_height)
                        y += row_height
                    y += 20

                for figure in section.select(cls='evidence-figure'):
                    img = figure.one(tag='img')
                    ratio = float(img.attrs['height']) / float(img.attrs['width'])
                    height = CW * ratio
                    if y + height > H - 145:
                        height = H - 145 - y
                    if height < 150:
                        raise ValueError('Evidence diagram lacks readable page space')
                    picture(images[img.attrs['src']], M, y, CW, height)
                    y += height + 12
                    captions = figure.select(tag='figcaption')
                    if captions:
                        y = text(captions[0].text(), M, y, size=10,
                                 bold=True, color=MUTED) + 14

                for result in section.select(cls='result'):
                    rule(y)
                    y += 12
                    items = result.select(tag='li')
                    for value in ([item.text() for item in items] or [result.text()]):
                        y = text('• ' + value, M, y, size=11, bold=True,
                                 leading=17) + 7
                for note in section.select(cls='case-note'):
                    y = text('• ' + note.text(), M, y+8, size=10,
                             bold=True, color=MUTED) + 8
                footer(page_number)
                page_number += 1
    pdf.save()
    print(f'Created {OUTPUT} ({page_count} pages)')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--font-dir', type=Path, default=Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts')
    parser.add_argument('--node-modules', type=Path)
    args = parser.parse_args()
    build(args.font_dir, args.node_modules)
