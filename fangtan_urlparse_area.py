#encoding=utf-8

import requests,time,re,json,sys,os

from include.agents import AGENTS
import random 
from lxml import html
import MySQLdb
from include.helpers import *

def random_proxy():
    length = len(AGENTS)
    index  = random.choice(range(0,length))
    return AGENTS[index]


def request_list(url = '',sleep = 0,num = 0,deep = 0, cookies = {}):
    agentheader = random_proxy()
    headers = {'content-type': 'text/html',
           'User-Agent': agentheader,
    }

    res = None
    try:
        res = requests.get(url,headers=headers,cookies=cookies,timeout=6)
        response = html.fromstring(res.text)    
        for k,v in zip(res.cookies.keys(),res.cookies.values()):                                                             
            cookies[k] = v

    except Exception,e:   #捕捉网络错误
        #print geturl
        print time.strftime("%Y-%m-%d %X", time.localtime()), url, '网络异常，重新拨号....'
        sys.stdout.flush()
        os.system('pppoe-stop')
        time.sleep(3)
        os.system('pppoe-start')
        time.sleep(10)
        deep += 1
        request_list(url,sleep,num,deep)

    #yanzhengma = retstr_replace(response.xpath(u'//*/div[@class="verify_info"]/@class'))
    if res.status_code == 200:   # and not yanzhengma:
        listurl = response.xpath(u'//div[@class="houseinfo-name"]/span/a/@href')
        print time.strftime("%Y-%m-%d %X", time.localtime()), len(listurl), url
        sys.stdout.flush()
        conn = MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',charset='utf8')
        conn.autocommit(1)
        cur = conn.cursor()
        cur.execute('use webspider')
        for con_url in listurl:
            con_url = 'http://bj.fangtan007.com' + con_url
            cur.execute("select * from ws_requesturl_data_area where url like '%s'" % (con_url))
            if cur.rowcount < 1:
                cur.execute("insert into ws_requesturl_data_area(website_id,created_at,crawled_at,url) values(16,%s,%s,'%s')" % (time.time(),0,con_url))
                print 'insert URL:',con_url
                sys.stdout.flush()
            else:
                print 'repeat URL:',con_url
                sys.stdout.flush()

        cur.close()
        conn.close()
        next_page = retstr_replace(response.xpath(u'//a[@title="下一页"][1]/@href'))
        #if next_page and num<4:    #调试用
        if next_page and num < 10:
            next_page = 'http://bj.fangtan007.com' + next_page
            print time.strftime("%Y-%m-%d %X", time.localtime()), '爬取深度报告:', next_page, 'sleep:', sleep, 'num:', num, 'deep:', deep
            sys.stdout.flush()
            num += 1
            deep += 1
            time.sleep(sleep)
            request_list(next_page,sleep,num,deep,cookies)
        else:
            print time.strftime("%Y-%m-%d %X", time.localtime()), '爬取完毕!'
            sys.stdout.flush()
            res.close()

    else:   #捕捉302 404跳转
        print time.strftime("%Y-%m-%d %X", time.localtime()), url, '302屏蔽，重新拨号....'
        sys.stdout.flush()
        if res:
            res.close()
        os.system('pppoe-stop')
        time.sleep(3)
        os.system('pppoe-start')
        time.sleep(10)
        deep += 1
        request_list(url,sleep,num,deep)


if __name__ == "__main__":
    geturl = [
    'http://bj.fangtan007.com/xiezilou/qiuzu/',
    'http://bj.fangtan007.com/qiuzu/shangpu/'
    ]
    for url in geturl:
        request_list(url,3,0)


