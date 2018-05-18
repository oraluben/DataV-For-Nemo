# Copyright (c) 2018 奥特虾
import datetime

import requests

from nemo.helper import *

payTimeList = []


def querry_database():
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT SUM(backer_money) FROM strawberry")
    results = cursor.fetchall()
    for row in results:
        dbMoney = row[0]
        return dbMoney


def querry_payTime():
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT pay_time FROM strawberry WHERE DATE_FORMAT(pay_time,'%m-%d') = DATE_FORMAT(now(),'%m-%d')")
    results = cursor.fetchall()
    for row in results:
        payTime = str(row[0])
        payTimeList.append(payTime)


def getDetail():
    url = 'https://wds.modian.com/api/project/detail'
    form = {
        'pro_id': pro_id
    }
    sign = getSign(form)
    form['sign'] = sign
    response = requests.post(url, form, headers=header).json()
    already_raised = response['data'][0]['already_raised']
    return already_raised


def getOrders():
    page = 1
    url = 'https://wds.modian.com/api/project/orders'
    a = True
    while a:
        form = {
            'page': page,
            'pro_id': pro_id
        }
        sign = getSign(form)
        form['sign'] = sign
        response = requests.post(url, form, headers=header).json()
        page += 1
        datas = response['data']
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        for data in datas:
            if date in data['pay_time']:
                if data['pay_time'] not in payTimeList:
                    user_id = data['user_id']
                    nickname = data['nickname']
                    backer_money = data['backer_money']
                    pay_time = data['pay_time']
                    db = connect_database()
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO strawberry VALUES (%s,%s,%s,%s,%s)",
                                   (pro_id, user_id, nickname, backer_money, pay_time))
                    db.commit()
                    msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
                          '[ERROR] 发现遗漏订单,数据补偿机制启动   ' + \
                          str(user_id) + '  ' + nickname + '  ' + str(backer_money) + '  ' + str(pay_time) + '\n'
                    print(msg)
                else:
                    a = False
            else:
                msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
                      '[WARNING] 数据异常，请及时处理\n'
                a = False
        with open('/var/log/FCC/dataCompensation.log', 'a+') as f:
            f.write(msg)
        print(msg)


def main():
    querry_payTime()
    if getDetail() != querry_database():
        getOrders()
    else:
        msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
              '[INFO] 例行巡检完成，本地数据正常\n'
        with open('/var/log/FCC/dataCompensation.log', 'a+') as f:
            f.write(msg)


if __name__ == '__main__':
    pro_id = 12767
    main()
