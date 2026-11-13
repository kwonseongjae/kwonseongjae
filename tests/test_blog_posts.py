import unittest

from scripts.sync_blog_posts import START, END, build_list, update_readme


class FeedTests(unittest.TestCase):
    def feed(self, link='https://jacks-aiblog.tistory.com/2'):
        return f'<rss><channel><item><title>학습 [예제]</title><link>{link}</link><pubDate>Fri, 13 Nov 2026 20:30:00 +0900</pubDate></item></channel></rss>'

    def test_replaces_only_the_selected_section(self):
        source = '소개\n' + START + '\n이전 글\n' + END + '\n프로젝트'
        result = update_readme(source, build_list(self.feed()))
        self.assertIn('학습 \\[예제\\]', result)
        self.assertTrue(result.startswith('소개\n'))
        self.assertTrue(result.endswith('\n프로젝트'))
        self.assertNotIn('이전 글', result)

    def test_untrusted_link_empty_feed_and_missing_markers_fail_closed(self):
        for value in [self.feed('https://evil.test/2'), '<rss><channel/></rss>']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_list(value)
        with self.assertRaises(ValueError):
            update_readme('소개만 있습니다', '새 글')


if __name__ == '__main__':
    unittest.main()
