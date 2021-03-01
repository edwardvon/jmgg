import scrapy
import re
import datetime
from ..items import JmggItem


class QuotesSpider(scrapy.Spider):
    name = "jmgg"
    start_urls = [
        'http://zyjy.jiangmen.cn/szqzccggg/index.htm',
        # 'http://zyjy.jiangmen.cn/pjqzccggg/index.htm',
    ]

    def parse(self, response):
        content_links = response.css('div.itemtw ul li a')
        yield from response.follow_all(content_links, self.parse_content)
        # for links in content_links:
        #     yield {
        #         "title": links.css("a::text").get(),
        #         "url": links.css("a::attr(href)").get(),
        #     }

        # try:
        #     page = int(re.search(r"index_(\d+)\.htm", response.url).group(1)) + 1
        # except AttributeError:
        #     page = 2
        # if page < 5:
        #     next_page = re.sub(r'index.*\.htm', f"index_{page}.htm", response.url)
        #     yield response.follow(next_page, callback=self.parse)

    def parse_content(self, response):
        pro = JmggItem()
        pro['name'] = response.css("div.neirong h1::text").get()
        # pro['project_code'] = re.search(r'项目编号：(<\w+>)?(.*?)<', response.text).group(2)
        time = response.css("div::text").re(r'发布时间：\s*([0-9]*?)-([0-9]*?)-([0-9]*?)\s([0-9]*?):(['
                                                           r'0-9]*?):([0-9]*?)\s')
        pro['last_updated'] = datetime.datetime(*[int(x) for x in time])
        # pro['agent'] = re.search(r'采购代理机构信息.*?名称：(<\w+>)?(.*?)[<]', response.text).group(2)
        # pro['client'] = re.search(r'采购人信息.*?名称：(<\w+>)?(.*?)<', response.text).group(2)
        yield pro
