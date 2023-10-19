import os
import requests
from requests import Session as req_Session
import time
import random
import re
from bs4 import BeautifulSoup


def randomly_gen_uspace_url() -> list:
    url_list = []
    for i in range(15):
        uid = random.randint(10000, 45000)
        url = "https://hostloc.com/space-uid-{}.html".format(str(uid))
        url_list.append(url)
    return url_list


def login(username: str, password: str) -> req_Session:
    headers = {
        "user-agent": "Mozilla/5.0",
        "origin": "https://hostloc.com",
        "referer": "https://hostloc.com/forum.php",
    }
    login_url = "https://hostloc.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
    login_data = {
        "fastloginfield": "username",
        "username": username,
        "password": password,
        "quickforward": "yes",
        "handlekey": "ls",
    }
    s = req_Session()
    res = s.post(url=login_url, data=login_data, headers=headers)
    res.raise_for_status()
    return s


def check_login_status(s: req_Session, number_c: int) -> bool:
    test_url = "https://hostloc.com/home.php?mod=spacecp"
    res = s.get(test_url)
    res.raise_for_status()
    res.encoding = "utf-8"
    test_title = re.findall("<title>(.*?)<\/title>", res.text)
    if len(test_title) != 0:
        if test_title[0] != "个人资料 -  全球主机交流论坛 -  Powered by Discuz!":
            print(f"第 {number_c} 个帐户登录失败！")
            return False
        else:
            print(f"第 {number_c} 个帐户登录成功！")
            return True
    else:
        print("未在用户设置页面找到标题，该页面可能存在错误！")
        return False


def print_current_points(s: req_Session):
    test_url = "https://hostloc.com/forum.php"
    res = s.get(test_url)
    res.raise_for_status()
    res.encoding = "utf-8"
    points = re.findall("积分: (\d+)", res.text)
    if len(points) != 0:
        print(f"帐户当前积分：{points[0]}")
    else:
        print("无法获取帐户积分，可能页面存在错误或者未登录！")
    time.sleep(7)


def get_formhash(s: req_Session) -> str:
    url = "https://hostloc.com/forum.php?mod=viewthread&tid=1218747&page=1#pid14626992"
    res = s.get(url)
    res.raise_for_status()
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, 'html.parser')
    formhash_element = soup.find('input', {'name': 'formhash'})
    if formhash_element:
        return formhash_element['value']
    else:
        print("未找到formhash")
        return None


def reply_to_thread(s: req_Session):
    formhash = get_formhash(s)
    if formhash:
        reply_url = "https://hostloc.com/forum.php?mod=post&action=reply&fid=XX&tid=1218747&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1"
        reply_data = {
            "message": "自己顶",
            "formhash": formhash,
            "usesig": "1",
            "subject": "",
        }
        headers = {
            "user-agent": "Mozilla/5.0",
            "origin": "https://hostloc.com",
            "referer": "https://hostloc.com/forum.php?mod=viewthread&tid=1218747&page=1#pid14626992",
        }
        res = s.post(url=reply_url, data=reply_data, headers=headers)
        res.raise_for_status()
        if "回复发布成功" in res.text:
            print("回复成功")
        else:
            print("回复失败")


def get_points(s: req_Session, number_c: int):
    if check_login_status(s, number_c):
        print_current_points(s)
        url_list = randomly_gen_uspace_url()
        for i in range(len(url_list)):
            url = url_list[i]
            try:
                res = s.get(url)
                res.raise_for_status()
                print(f"第 {i + 1} 个用户空间链接访问成功")
                time.sleep(5)
            except Exception as e:
                print(f"链接访问异常：{str(e)}")
            continue
        print_current_points(s)
        reply_to_thread(s)  # 添加回复功能


if __name__ == "__main__":
    username = os.environ["HOSTLOC_USERNAME"]
    password = os.environ["HOSTLOC_PASSWORD"]

    user_list = username.split(",")
    passwd_list = password.split(",")

    if len(user_list) != len(passwd_list):
        print("用户名与密码个数不匹配，请检查环境变量设置是否错漏！")
    else:
        print(f"共检测到 {len(user_list)} 个帐户，开始获取积分")
        print("*" * 30)

        for i in range(len(user_list)):
            try:
                s = login(user_list[i], passwd_list[i])
                get_points(s, i + 1)
                print("*" * 30)
            except Exception as e:
                print(f"程序执行异常：{str(e)}")
                print("*" * 30)
            continue

        print("程序执行完毕，获取积分过程结束")
