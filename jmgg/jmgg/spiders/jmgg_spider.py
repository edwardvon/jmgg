import scrapy
import re
import datetime
import os
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
        price = re.search(r'采购预算|预算金额(（元）)?(<\w+>)?：(<\w+>)?(.*?)(（|</p)', response.text).group(4)
        price = re.sub(r'(。|&yen;|&nbsp;|￥|,|\s|元|<[\w/]+>)', "", price)
    except AttributeError:
        price = None
    try:
        price = float(price)
    except ValueError:
        pass
    except TypeError:
        pass
    return price


def get_deadline(response):
    p = response.css("div.newsCon")
    try:
        deadline = re.search(r'(截止时间|磋商时间)[、：和](.*?<u>)?((\d|&nbsp;).*?)[。|（]', response.text).group(3)
        # 将截止时间中间的标签、空格等去除
        deadline = re.sub(r'<.*?>|\s|&nbsp;', "", deadline)
        time = re.findall(r'\d+', deadline)
        deadline = datetime.datetime(*[int(x) for x in time])
    except AttributeError:
        deadline = None
    except TypeError:
        deadline = None
    except ValueError:
        deadline = None
    return deadline


def get_agent(response):
    try:
        # '联系.*?'匹配公告结尾机构信息，避免匹配到正文中的“采购代理机构”而获取到采购人名称
        # agent = re.search(r'联系.*?采购代理机构(信息)?.*?名(\s|&nbsp;){0,4}称：(<\w+>)?(.*?)(<|&nbsp;|。|，|；)', response.text).group(4)

        # 新匹配方式，从最底下项目联系人处获取采购代理名称；命中率比前一行写法高一点。
        # (>|：|&nbsp;)匹配名称前可能的字符
        agent = re.search(r'项目联系人.*(>|：|&nbsp;)(.*?公司)(<|；|。)', response.text).group(2)
    except AttributeError:
        agent = None
    return agent


def get_client(response):
    try:
        # “名称”之间适配空格和&nbsp;
        client = re.search(r'采购人(信息)?.*?名(\s|&nbsp;){0,6}称：(<\w+>)?(.*?)(<|&nbsp;|；|。)', response.text).group(4)
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


def gentle_file(path, filename, content, decode='wb'):
    if not os.path.exists(path):
        os.mkdir(path)
    with open(f'{path}/{filename}', decode) as f:
        f.write(content)


def gentle_html(response, area, num):
    path = f'html/{area}'
    filename = f'{num}.html'
    gentle_file(path, filename, response.body)


def download_pdf(response, area, num):
    path = f'html/{area}'
    filename = f'{num}.pdf'
    gentle_file(path, filename, response.body)


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
            if re.search(r'更正|补充|澄清|论证|单一来源|调整公告|预审公告', title):
                yield response.follow(url, self.parse_other)
            else:
                yield response.follow(url, self.parse_content)
        next_page = response.css("div.pagesite").xpath("//a[contains(text(),'下一页')]/@onclick").re(
            r"\'.*?\.htm")[0].replace("\'", "")
        yield response.follow(f'http://zyjy.jiangmen.cn/cggg/{next_page}', self.parse)

    def parse_content(self, response):
        pro = JmggItem()
        pro['name'] = response.css("div.neirong h1::text").get()
        pro['project_code'] = get_project_code(response)
        pro['price'] = get_price(response)
        pro['deadline'] = get_deadline(response)
        pro['agent'] = get_agent(response)
        pro['client'] = get_client(response)
        pro['area'] = get_area(response.url)
        time = response.css("div::text").re(r'发布时间：\s*([0-9]*?)-([0-9]*?)-([0-9]*?)\s([0-9]*?):(['
                                            r'0-9]*?):([0-9]*?)\s')
        pro['pubdate'] = datetime.datetime(*[int(x) for x in time])
        pro['url'] = response.url
        pro.save()
        # 处理html文件创建和pdf下载
        num = re.search(r'/(\d+)\.htm', response.url).group(1)
        area = re.search(r'/(\w+)zccggg', response.url).group(1)
        gentle_html(response, area, num)
        try:
            pdf_url = re.search(r'附件.*?href=\"(.*?)\"', response.text).group(1)
            pro['pdf'] = pdf_url
            # TODO:完成pdf下载方法。反正都是byte写文件，问题就是路径怎么传参
            # yield response.follow(pdf_url, self.parse_pdf)
        except AttributeError:
            pass
        yield pro

    def parse_other(self, response):
        num = re.search(r'/(\d+)\.htm', response.url).group(1)
        area = re.search(r'/(\w+)zccggg', response.url).group(1)
        gentle_html(response, area, num)

    def parse_pdf(self, response):
        pass
