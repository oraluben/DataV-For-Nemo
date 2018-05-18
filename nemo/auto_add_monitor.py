import requests
from lxml import etree

from nemo.helper import *

infoList = []
infoDict = {}


def get_taskList():  # 从数据库查询已有任务列表
    taskList = []
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT pro_id FROM monitor_proid")
    results = cursor.fetchall()
    for pro_id in results:
        pro_id = pro_id[0]
        taskList.append(pro_id)
    return taskList


def check_task(user_id):  # 从摩点用户主页获取已经开始的任务列表
    proidList = []
    url = 'https://me.modian.com/user?type=index&id='
    url = url + str(user_id)
    html = requests.get(url).content
    selector = etree.HTML(html)
    infos = selector.xpath('//*[@class="prothumb"]/a[1]')
    for info in infos:
        projectUrl = info.xpath('@href')[0].split('.html')[0]
        proid = projectUrl[34:]
        proidList.append(proid)
    return proidList


def add_task(pro_id, idol_name, user_id):  # 自动添加任务至数据库
    db = connect_database()
    cursor = db.cursor()
    for pro_id in check_task(user_id):
        if pro_id not in get_taskList():
            response = get_response(pro_id)
            status = 0
            pro_name = response['data'][0]['pro_name']
            already_raised = response['data'][0]['already_raised']
            cursor.execute("insert into monitor_proid values (%s,%s)", (idol_name, pro_id))
            cursor.execute("insert into monitor values (%s,%s,%s,%s,%s)",
                           (idol_name, pro_id, pro_name, already_raised, status))
            db.commit()
            msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  ' + \
                  '[WARNING] ' + pro_name + ' ' + pro_id + ' 已上线\n'
            write(msg)


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


def add_task_start():  # 自动添加任务的主函数
    for user_id in infoList:
        idol_name = infoDict[user_id]
        for pro_id in check_task(user_id):
            add_task(pro_id, idol_name, user_id)


def main():  # 主程序函数
    querry_database()
    add_task_start()


if __name__ == '__main__':
    main()
