"""티스토리 RSS의 최신 학습 글을 프로필에 반영한다."""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit

BLOG = 'jacks-aiblog.tistory.com'
START = '<!-- BLOG-POST-LIST:START -->'
END = '<!-- BLOG-POST-LIST:END -->'


def build_list(data):
    items = ET.fromstring(data).findall('./channel/item')[:5]
    if not items:
        raise ValueError('RSS에 공개 글이 없어 기존 목록을 보존합니다')
    lines = []
    for item in items:
        link = (item.findtext('link') or '').strip()
        p = urlsplit(link)
        if p.scheme != 'https' or p.netloc != BLOG or p.query or p.fragment or not re.fullmatch(r'/[1-9][0-9]*', p.path):
            raise ValueError('새 블로그의 공개 글 주소가 아닙니다')
        title = ' '.join((item.findtext('title') or '').split())
        if not title:
            raise ValueError('글 제목이 없습니다')
        title = html.escape(title.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]'))
        date = parsedate_to_datetime(item.findtext('pubDate') or '').date().isoformat()
        lines.append(f'- [{title}]({link}) <sub>{date}</sub>')
    return '\n'.join(lines)


def update_readme(source, posts):
    if source.count(START) != 1 or source.count(END) != 1 or source.index(END) < source.index(START):
        raise ValueError('최신 글 목록의 시작·끝 위치를 확인할 수 없습니다')
    before, rest = source.split(START)
    _, after = rest.split(END)
    return before + START + '\n' + posts + '\n' + END + after


def main():
    request = urllib.request.Request(f'https://{BLOG}/rss', headers={'User-Agent': 'LearningBlogFeed/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('RSS 응답이 허용 크기를 넘었습니다')
    path = Path(__file__).resolve().parents[1] / 'README.md'
    original = path.read_text(encoding='utf-8')
    updated = update_readme(original, build_list(data))
    path.write_text(updated, encoding='utf-8')


if __name__ == '__main__':
    main()
