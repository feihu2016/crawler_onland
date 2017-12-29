#encoding=utf-8

import requests,time,re,json,sys,os,random

reload(sys)
sys.setdefaultencoding('utf-8')

global_path = "/data/server/www/haozu/haozu_online/crawler/"
sys.path.append(global_path)

import MySQLdb
from misc.helpers import *

class fangtan007_init:
    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',charset='utf8')
        self.conn.autocommit(1)
        self.cur = self.conn.cursor()
        self.cur.execute('use crawl')
        self.ft_print('数据库初始化！')


    def run(self):
        self.cur.execute('update ws_login_users set use_at=0, deny_at=0')
        self.ft_print('ws_login_users表： %s个账号全部启用。' % (self.cur.rowcount))
        logpath = '/data/logs/haozu/crawler/'
        logname = 'fangtan_contentparse_%s.log' % (time.strftime("%Y%m%d", time.localtime()))
        shell_comm = 'nohup /usr/bin/python /data/server/www/haozu/haozu_online/crawler/fangtan007/fangtan_contentparse.py >> %s%s 2>&1 &' % (logpath,logname)
        os.system("cd /data/server/www/haozu/haozu_online/crawler/fangtan007")
        os.system(shell_comm)
        self.ft_print(shell_comm)

    def ft_print(self, data):
        print time.strftime("%Y-%m-%d %X", time.localtime()), data
        sys.stdout.flush()


if __name__ == "__main__":    
    fangtan = fangtan007_init()
    fangtan.run()



