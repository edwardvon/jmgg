import scrapy
import re
import datetime
from ..items import JmggItem


def get_project_code(response):
    try:
        # ([\w\-\_]*?) 限定编号为数字、字母、短横线、下划线
        code = re.search(r'(项目编号|招标编号|采购编号)：(<\w+>)?([\w\-\_]*?)[<|）（]', response.text).group(3)
    except AttributeError:
        # code = re.search(r'招标编号：(<\w+>)?(.*?)[<|）]', response.text).group(2)
        code = None
    return code


def get_price(response):
    try:
        price = re.search(r'采购预算|预算金额(（元）)?(<\w+>)?：(<\w+>)?(.*?)[（|<]', response.text).group(4)
    except AttributeError:
        price = None
    return price


def get_deadline(response):
    try:
        deadline = re.search(r'截止时间[、：](.*?<u>)?(.*?)[。|（]', response.text).group(2)
        # 将截止时间中间的标签、空格等去除
        deadline = re.sub(r'<.*?>|\s|&nbsp;', "", deadline)
    except AttributeError:
        deadline = None
    return deadline


def get_agent(response):
    try:
        # '联系.*?'匹配公告结尾机构信息，避免匹配到正文中的“采购代理机构”而获取到采购人名称
        agent = re.search(r'联系.*?采购代理机构(信息)?.*?名\s{0,4}称：(<\w+>)?(.*?)[<；，。]', response.text).group(3)
    except AttributeError:
        agent = None
    return agent


def get_client(response):
    try:
        client = re.search(r'采购人(信息)?.*?名[\s&nbsp;]{0,4}称：(<\w+>)?(.*?)<', response.text).group(3)
    except AttributeError:
        client = None
    return client


AREA = {
    'szq': '市直',
    'pjq': '蓬江区',
    'jhq': '江海区',
    'xhq': '新会区',
    'tss': '台山市',
    'kps': '开平市',
    'eps': '恩平市',
    'hss': '鹤山市'
}


def get_area(url):
    area = re.search(r"/(\w{3})zccggg", url).group(1)
    return AREA[area]


class QuotesSpider(scrapy.Spider):
    name = "jmgg"
    start_urls = [
        'http://zyjy.jiangmen.cn/cggg/index.htm',
        # 'http://zyjy.jiangmen.cn/szqzccggg/index.htm',
        # 'http://zyjy.jiangmen.cn/pjqzccggg/index.htm',
    ]

    def parse(self, response):
        content_links = response.css('div.itemtw ul li a')
        for links in content_links:
            # 用title属性值而不是text，避免因自动collapse获取不到全称
            title = links.css("a::attr(title)").get()
            url = links.css("a::attr(href)").get()
            if re.search(r'更正|补充|澄清|论证|单一来源|调整公告', title):
                yield {
                    "title": title,
                    "url": url
                }
            else:
                yield response.follow(url, self.parse_content)

    def parse_content(self, response):
        pro = JmggItem()
        pro['name'] = response.css("div.neirong h1::text").get()
        pro['project_code'] = get_project_code(response)
        # pro['price'] = get_price(response)
        # pro['deadline'] = get_deadline(response)
        # pro['agent'] = get_agent(response)
        # pro['client'] = get_client(response)
        # pro['area'] = get_area(response.url)
        # time = response.css("div::text").re(r'发布时间：\s*([0-9]*?)-([0-9]*?)-([0-9]*?)\s([0-9]*?):(['
        #                                     r'0-9]*?):([0-9]*?)\s')
        # pro['last_updated'] = datetime.datetime(*[int(x) for x in time])
        yield pro
