#encoding=utf-8

import requests,time,re,json,sys,os,random

reload(sys)
sys.setdefaultencoding('utf-8')

from include.agents import AGENTS
from lxml import html
import MySQLdb
from include.helpers import *

from selenium import webdriver

class fangtan007:
    def __init__(self, url = ''):
        self.host_url = url
        self.userid = ()  # (id, username, password)
        self.website_id = 16
        self.__initobject()

    def __initobject(self):
        agentheader = self.random_proxy()
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        headers = { 
                    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
                    "Connection": "keep-alive"
                    }
        for key,value in headers.items():
            capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
            cap[capability_key] = value

        cap["phantomjs.page.settings.loadImages"] = False
        cap["phantomjs.page.settings.disk-cache"] = True
        cap["phantomjs.page.settings.userAgent"] = agentheader
        self.driver = webdriver.PhantomJS(desired_capabilities=cap)
        self.driver.set_page_load_timeout(60)  #两个一块设置才有效
        self.driver.set_script_timeout(60)
        self.conn = MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',charset='utf8')
        self.conn.autocommit(1)
        self.cur = self.conn.cursor()
        self.cur.execute('use webspider')

    def random_proxy(self):
        length = len(AGENTS)
        index  = random.choice(range(0,length))
        return AGENTS[index]

    #登录并产生driver句柄
    def gethost_onland(self):
        if self.userid:
            self.get_password(self.userid[0])
        else:
            self.get_password()

        try:
            print time.strftime("%Y-%m-%d %X", time.localtime()), '登录URL:', self.host_url, '登录账号:', self.userid
            sys.stdout.flush()
            self.driver.get(self.host_url)
            time.sleep(3)
            username_xpath = self.driver.find_element_by_xpath('//input[@id="userName"]')
            password_xpath = self.driver.find_element_by_xpath('//input[@id="password"]')
            button_xpath = self.driver.find_element_by_xpath(u'//input[@value="登 录"]')
            username_xpath.send_keys(self.userid[1])
            password_xpath.send_keys(self.userid[2])
            button_xpath.click()
            time.sleep(3)
            if u'管理' in self.driver.title:
                print time.strftime("%Y-%m-%d %X", time.localtime()), '登录成功！', self.driver.current_url
                sys.stdout.flush()
            else:
                print time.strftime("%Y-%m-%d %X", time.localtime()), '登录失败！', self.driver.current_url
                sys.stdout.flush()
                self.__close()
                self.change_ip()
                self.__initobject()
                self.gethost_onland()

        except Exception,e:
            print time.strftime("%Y-%m-%d %X", time.localtime()), '登录错误并重新加载和更换ip！', e
            sys.stdout.flush()
            #self.__close()
            self.change_ip()
            self.__initobject()
            self.gethost_onland()
    
    #更新旧的userid，并获取一个新的账号
    def get_password(self, old_userid = 0):
        if old_userid > 0:
            self.cur.execute("update ws_login_users set deny_at=%s where id=%s" % (time.time(), old_userid))

        self.cur.execute("select id,username,password from ws_login_users where deny_at=0 and website_id=%s limit 1" % (self.website_id))
        if self.cur.rowcount > 0:
            self.userid = self.cur.fetchone()
            self.cur.execute("update ws_login_users set use_at=%s where id=%s" % (time.time(), self.userid[0]))
            print time.strftime("%Y-%m-%d %X", time.localtime()), '获取登录账号:', self.userid
            sys.stdout.flush()
        else:
            print time.strftime("%Y-%m-%d %X", time.localtime()), '已没有可用登录账号，爬虫停止。'
            sys.stdout.flush()
            exit()      


    def change_ip(self):
        print time.strftime("%Y-%m-%d %X", time.localtime()), '开始重新拨号....'
        sys.stdout.flush()
        os.system('pppoe-stop')
        time.sleep(3)
        os.system('pppoe-start')
        time.sleep(10)
        print time.strftime("%Y-%m-%d %X", time.localtime()), '完成重新拨号....'
        sys.stdout.flush()

    def run(self):
        while True:
            self.cur.execute("select id,url from ws_requesturl_data_area where crawled_at=0 limit 1")
            if self.cur.rowcount>0:
                content_url = self.cur.fetchone()
                print time.strftime("%Y-%m-%d %X", time.localtime()), content_url[1]
                sys.stdout.flush()
                item = {}
                item['url'] = content_url[1]
                item['created_at'] = date_timestamp()
                item['updated_at'] = date_timestamp()
                item['crawled_at'] = date_today()
                try:
                    self.driver.get(content_url[1])
                    time.sleep(3)
                    element = self.driver.find_element_by_xpath('//span[@id="tel"]')
                except Exception, e:
                    self.change_ip()
                    self.gethost_onland()
                    continue
                item['guwen_phone'] = element.text
                print time.strftime("%Y-%m-%d %X", time.localtime()),'进入登录状态数据分析：', self.driver.current_url
                sys.stdout.flush()

                try:
                    element = self.driver.find_element_by_xpath('//div[@class="info-right-div"]/ul/li[1]/span[1]')
                except Exception, e:
                    item['guwen'] = ''
                item['guwen'] = element.text

                try:
                    element = self.driver.find_element_by_xpath('//div[@class="detail-name"]/h1')
                except Exception, e:
                    item['title'] = ''
                item['title'] = element.text

                try:
                    element = self.driver.find_element_by_xpath('//div[@class="detail-intsum"]')
                except Exception, e:
                    item['pub_date'] = '1990-01-01'
                item['pub_date'] = re.search(r'(\d+-\d+-\d+)', element.text).group(1).strip() if re.search(r'', element.text)  is not None else ''

                try:
                    element = self.driver.find_element_by_xpath('//span[@class="fontcolorfa fontw"]')
                except Exception, e:
                    item['clicks'] = 0
                item['clicks'] = element.text                

                pinyin = re.search(r'(\w+).fangtan007.com', self.host_url).group(1)
                city = cityInfo(pinyin)
                item['city_id'] = city['city_id']
                item['city_name'] = city['city_name']

                item['rent_price'] = 0
                item['rent_price_unit'] = ''
                item['area'] = 0                
                item['address'] = ''

                try:
                    element = self.driver.find_element_by_xpath('//div[@class="detail-info-left"]/ul/span')
                except Exception, e:
                    item['district_name'] = ''
                split_text = re.split('-', element.text)
                item['district_name'] = split_text[1].strip() if len(split_text)>1 else ''                

                try:
                    element = self.driver.find_elements_by_xpath('//div[@class="detail-info-left"]/ul/li')
                except Exception, e:
                    pass

                for ele in element:
                    ele_text = ele.text
                    if re.search(u'价格', ele_text):
                        this_search = re.search('(\d+)', ele_text)
                        item['rent_price'] = this_search.groups()[0] if len(this_search.groups())>0 else 0
                    elif re.search(u'面积', ele_text):
                        this_search = re.search('(\d+)', ele_text)
                        item['area'] = this_search.groups()[0] if len(this_search.groups())>0 else 0
                    elif re.search(u'地址', ele_text):
                        this_search = re.split('\r|\n', ele_text)
                        item['address'] = this_search[1] if len(this_search)>1 else ''


                item['info_type'] = 2
                self.save_data(item, content_url[0])

            else:
                print time.strftime("%Y-%m-%d %X", time.localtime()), '数据已经分析完毕，爬虫停止。'
                sys.stdout.flush()
                exit()  


    def save_data(self, item = {}, data_id = 0):
        fields = ''
        values = ''
        insertmode = 'insert into ws_house_info_16(%s) values(%s)'
        for k in item:
            fields += '`' + k + '`,'
            if k== 'created_at':
                values += '%s,' % item[k]
            elif k== 'updated_at':
                values += '%s,' % item[k]
            #elif k== 'crawled_at':
            #    values += '%s,' % item[k]
            elif k== 'city_id':
                values += '%s,' % item[k]
            elif k== 'rent_price':
                values += '%s,' % item[k]
            elif k== 'area':
                values += '%s,' % item[k]
            elif k== 'userage':
                values += '%s,' % item[k]
            elif k== 'istop':
                values += '%s,' % item[k]
            elif k== 'iscream':
                values += '%s,' % item[k]
            elif k== 'info_type':
                values += '%s,' % item[k]
            elif k=='clicks':
                values += '%s,' % item[k]
            else:
                values += '"%s",' % item[k]


        fields = fields.rstrip(',')
        values = values.rstrip(',')
        insertsql = insertmode % (fields, values)
        print item
        print time.strftime("%Y-%m-%d %X", time.localtime()), insertsql
        sys.stdout.flush()
        self.cur.execute(insertsql)
        update_sql = "update ws_requesturl_data_area set crawled_at=%s where id=%s" % (time.time(), data_id)
        print time.strftime("%Y-%m-%d %X", time.localtime()), update_sql
        sys.stdout.flush()
        self.cur.execute(update_sql)

    def __close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        if self.driver:
            self.driver.delete_all_cookies()
            self.driver.quit()

    def __del__(self):
        self.__close()
        print time.strftime("%Y-%m-%d %X", time.localtime()), '已完成类卸载。'


if __name__ == "__main__":
    login_url = 'http://bj.fangtan007.com/my/login'
    fangtan = fangtan007(login_url)
    fangtan.run()



