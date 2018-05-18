import hashlib
import time
import urllib.parse

import pymysql

from nemo.config import config

mysql_conn = config['conn']


def write(msg):  # 记录日志文件的函数
    with open('/var/log/FCC/monitor.log', 'a+') as f:
        f.write(msg)


def connect_database():  # 连接到服务器数据库
    from nemo.config import config
    mysql_conn = config['conn']
    db = pymysql.connect(**mysql_conn)
    cursor = db.cursor()
    return db


def time_format_conversion(dt):  # 将时间转化为时间戳的函数
    timeStamp = time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))
    return timeStamp


def getSign(ret):  # 生成签名的函数
    tuple = sorted(ret.items(), key=lambda e: e[0], reverse=False)
    md5_string = urllib.parse.urlencode(tuple).encode(encoding='utf_8', errors='strict')
    md5_string += b'&p=das41aq6'
    sign = hashlib.md5(md5_string).hexdigest()[5: 21]
    return sign


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)'
                        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
