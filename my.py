from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import csv
import pandas as pd
import time
import re
import random
from multiprocessing.dummy import Pool,Lock

def get_content_guba(url,visited_urls):
    '''
    获取网址开头为“guba”帖子内容与时间
    :param url: 帖子网址
    :return: 帖子内容与时间
    '''
    l = []

    current_url = check_dejavu(url, visited_urls)
    if current_url is None:
        return None

    bro.get(url)  # 打开页面
    response = bro.page_source
    tree = etree.HTML(response)
    try:
        try:
            time = tree.xpath('//*[@id="newscontent"]/div[2]/div[2]/div/div[2]')[0]
        except:
            time = ''
    except:
        time = ''
    l.append(time)
    try:
        content = tree.xpath('//*[@id="newscontent"]/div[4]/div//text()')
        content = ','.join(content).strip()
        content = process_gbk(content)
    except:
        content = ''
    l.append(content)
    return l


def get_content_caifuhao(url,visited_urls):
    '''
    获取网址开头为“caifuhao”帖子内容与时间
    :param url: 帖子网址
    :return: 帖子内容与时间
    '''
    l = []

    current_url = check_dejavu(url, visited_urls)
    if current_url is None:
        return None

    bro.get(url)  # 打开页面
    response = bro.page_source
    tree = etree.HTML(response)
    try:
        time = tree.xpath('//*[@id="main"]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[2]/text()')[0]
    except:
        time = ''
    l.append(time)
    try:
        content = tree.xpath('//*[@id="main"]/div[2]/div[1]/div[1]/div[1]/div[3]//text()')
        content = ','.join(content).strip()
        content = process_gbk(content)
    except:
        try:
            content = tree.xpath('//*[@id="main"]/div[2]/div[1]/div[1]/div[1]/div[3]//text()')
            content = ','.join(content).strip()
            content = process_gbk(content)
        except:
            content = ''
    l.append(content)
    return l


def process_gbk(content):
    '''
    去掉无法识别的字符
    :param content: 要处理的内容
    :return: 处理后的内容
    '''
    content = re.sub(
        u'([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b])',
        '', content)
    return content

def get_list(file):
    '''
    去掉无法识别的字符
    :param content: 获取股票代码并处理成唯一值
    :return: 股票代码列表
    '''
    # 读取 Excel 文件
    excel_file = pd.ExcelFile(file)

    # 获取 'POP_up 400' 工作表的第二列数据
    pop_up_sheet = excel_file.parse('POP_up 400')
    pop_up_codes = pop_up_sheet.iloc[:, 1].astype(str).str.zfill(6).tolist()

    # 获取 'PETTM_up 400' 工作表的第二列数据
    pettm_up_sheet = excel_file.parse('PETTM_up 400')
    pettm_up_codes = pettm_up_sheet.iloc[:, 1].astype(str).str.zfill(6).tolist()

    # 合并两个工作表的代码列
    code = pop_up_codes + pettm_up_codes
    # 使用集合去除重复元素
    unique_codes = list(set(code))
    return unique_codes

def check_dejavu(url,visited_urls):
    """
    处理重定向并进行URL比较
    :param url: 当前页面的URL
    :param visited_urls: 已经访问过的URL集合
    :return: 处理后的URL
    """
    # 检查当前页面是否已经访问过
    if url in visited_urls:
        print(f"Skipping already visited page: {url}")
        return None  # 返回None表示不需要继续处理

    # 进行重定向处理
    bro.get(url)
    current_url = bro.current_url

    # 检查重定向后的页面是否已经访问过
    if current_url in visited_urls:
        print(f"Skipping already visited page (after redirect): {current_url}")
        return None

    visited_urls.add(current_url)  # 将当前页面加入已访问集合
    return current_url





def start_spyder(codes):
    '''
    爬虫主体程序
    :param code: 股票代码
    :return: None
    '''
    visited_urls = set()
    for code in codes:
    # 定义csv字段，存储评论信息至comments/股票代码.csv
        filepath = f'../comments/{code}.csv'
        csvf = open(filepath, 'a+', newline='', encoding='gb18030', errors='ignore')
        fieldnames = ['title', 'author', 'read', 'comment_number', 'time', 'content', 'url']
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        url = f'http://guba.eastmoney.com/list,{code},99.html'
        bro.get(url)  # 打开页面
        response = bro.page_source
        tree = etree.HTML(response)
        try:
            page_num = tree.xpath('//*[@id="mainlist"]/div/ul/li[1]/ul/li[position() = last() - 1]/a/span/text()')[0]#使用XPath的last()函数来选择最后一个li元素
        except:
            print(url)
            continue
        for i in range(1, int(page_num) + 1):
            page_url = f'http://guba.eastmoney.com/list,{code},99_{i}.html'
            #time.sleep(random.uniform(1, 5))
            current_url = check_dejavu(page_url, visited_urls)
            if current_url is None:
                continue
            bro.get(page_url)  # 打开页面
            page_response = bro.page_source
            tree = etree.HTML(page_response)
            for n in range(1, 80):  # 每一页顶多80个帖子
                try:
                    title_element = tree.xpath(f'//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr[{n}]/td[3]/div/a')[0]  # tr表示行  td表示列
                except:
                    title_element = ''
                try:
                    title = title_element.get('title', '')
                except:
                    title = ''
                try:
                    url_1 = f'http:{title_element.get("href", "")}.html'
                except:
                    url_1 = ''
                try:
                    read_num = tree.xpath(f'//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr[{n}]/td[1]/div/text()')[0]
                except:
                    read_num = ''
                try:
                    comment_number = tree.xpath(f'//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr[{n}]/td[2]/div/text()')[
                        0]  # 从根节点开始搜索的地址
                except:
                    comment_number = ''
                try:
                    author = tree.xpath(f'//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr[{n}]/td[4]/div/a/text()')[0]
                except:
                    author = ''
                try:
                    time_1 = tree.xpath(f'//*[@id="mainlist"]/div/ul/li[1]/table/tbody/tr[{n}]/td[5]/div/text()')[0]
                except:
                    time_1 = ''

                data_info = {
                    'title': title,
                    'author': author,
                    'read': read_num,
                    'comment_number': comment_number,
                    'time': time_1,
                    'content': '',
                    'url': url_1
                }

                if url_1[7:11:] == 'guba':  # https://guba.eastmoney.com/news,600418,1374855665.html
                    # 获取帖子内容
                    temp = get_content_guba(url_1,visited_urls)
                    if temp is None:
                        continue
                    # data_info['time'] = temp[0]
                    data_info['content'] = temp[1]
                    writer.writerow(data_info)
                    # 判断，如果帖子评论数为0，则不需要调用获取评论方法

                elif url_1[
                     7:15:] == 'caifuhao':  # https://caifuhao.eastmoney.com/news/20231106112904080831020?from=guba&name=5rGf5reu5rG96L2m5ZCn&gubaurl=aHR0cHM6Ly9ndWJhLmVhc3Rtb25leS5jb20vbGlzdCw2MDA0MTgsOTlfMy5odG1s
                    temp = get_content_caifuhao(url_1,visited_urls)
                    if temp is None:
                        continue
                    # data_info['time'] = temp[0]
                    data_info['content'] = temp[1]
                    writer.writerow(data_info)

                    # 有些帖子是视频，遇到直接跳过，或者url为空的情况也是直接跳过
                    # 比如https://caifuhao.eastmoney.com/news/20230729113724781112830
                else:
                    continue

        print(filepath, '写入完成！！！')
        print('===============================================================================')
        # 关闭csv
        csvf.close()

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    # 实现无可视化界面的操作（无头浏览器）
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # 不加载图片
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument('referer=https://guba.eastmoney.com/')#Referer是 HTTP 请求头中的一个字段，它包含了当前请求页面的来源地址，即用户在浏览器中点击链接或提交表单前所在的页面的 URL

    bro = webdriver.Chrome(
        executable_path=r'E:\guba_spider-main\chromedriver-win64\chromedriver-win64\chromedriver.exe',
        options=chrome_options)
    codes =get_list('stock_num.xlsx')
    pool = Pool(8)  # 进程开多了跑久了selenium会报Timeout错误（我开8个和6个就报错了）
    pool.map(start_spyder, [codes])
    pool.close()
    pool.join()
    #start_spyder(codes)

    bro.quit()#在循坏外关闭，防止浏览器在任务执行期间被多次关闭，减少潜在问题