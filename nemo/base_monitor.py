import requests

from nemo.helper import *



def get_response(pro_id):  # 从rankings接口获取数据
    db = connect_database()
    cursor = db.cursor()
    url = 'https://wds.modian.com/api/project/detail'
    form = {
        'pro_id': pro_id
    }
    sign = getSign(form)
    form['sign'] = sign
    response = requests.post(url, form, headers=header).json()
    return response


def querry_database():  # 从数据库查询正在进行中的任务
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT pro_id FROM monitor WHERE status = 0")
    results = cursor.fetchall()
    msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
          '[INFO] 数据更新完成\n'
    write(msg)
    for pro_id in results:
        pro_id = pro_id[0]
        check_data(pro_id)


def check_data(pro_id):  # 更新各竞争对手集资总额数据
    db = connect_database()
    cursor = db.cursor()
    response = get_response(pro_id)
    pro_name = response['data'][0]['pro_name']
    already_raised = response['data'][0]['already_raised']
    endtime = time_format_conversion(response['data'][0]['end_time'])
    if float(endtime) > float(time.time()):
        status = 0
    else:
        cursor.execute("update monitor set status = 1 where pro_id = (%s)", (pro_id))
        msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
              '[WARNING] ' + pro_name + ' ' + pro_id + ' 已结束\n'
        write(msg)
    cursor.execute("update monitor set already_raised = (%s) where pro_id = (%s)", (already_raised, pro_id))
    db.commit()
    db.close()


def main():  # 主程序函数
    querry_database()


if __name__ == '__main__':
    main()
