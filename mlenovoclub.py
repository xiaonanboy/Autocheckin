import requests
import time
import json
import urllib3
import re
import configparser
import base64

urllib3.disable_warnings()
def checkin(account,password):
    retab = '0'
    url_login = 'https://reg.lenovo.com.cn/auth/v2/doLogin'
    url_signlist = 'https://mclub.lenovo.com.cn/signlist'
    url_sign = 'https://mclub.lenovo.com.cn/signadd'
    url_jointask = 'https://mclub.lenovo.com.cn/signchallengetask'
    headers_login = {
        'Host': 'reg.lenovo.com.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://reg.lenovo.com.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2Fhome.html%3Fmod%3Dspace%26do%3Dprofile%26mycenter%3D1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    # 用户密码base64加密
    passw = str(base64.b64encode(password.encode('utf-8')),'utf-8')
    data_login = {
        'account':account,
        'password':passw,
        'ps': '1',
        'ticket':'5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3',
        'codeid':'',
        'code':'',
        'slide':'v2',
        'st':'1584880930109'
    }

    headers_signlist = {
        'Host': 'mclub.lenovo.com.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    headers_sign= {
        'Host': 'mclub.lenovo.com.cn',
        'Connection': 'keep-alive',
        'Content-Length': '47', #task57
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://mclub.lenovo.com.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://mclub.lenovo.com.cn/signlist/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    session = requests.session()
    response_login = session.post(url_login, params=data_login, headers=headers_login, verify=False)
    result_login = json.loads(response_login.content)
    if result_login['ret'] == '0' :
        dict_cookies=response_login.cookies.get_dict()
        response_signlist = session.get(url_signlist,cookies=dict_cookies,headers=headers_signlist,verify=False)
        token_utf8 = response_signlist.content.decode("utf-8")
        result_token = re.search('CONFIG.token\s=\s"\w{40}',token_utf8) #获取随机token
        myToken = result_token.group()[-40:]
        result_taskcontinue = re.search('><b>.{1,8}',token_utf8)
        taskcontinue = result_taskcontinue.group()[-8:]

        data_sign = {
            '_token': myToken
        }

        data_jointask = {
        'task_id': '3',
        '_token': myToken
        }

        response_sign = session.post(url_sign,data=data_sign,headers=headers_sign,verify=False)
        result_signa = response_sign.content.decode("unicode_escape")# unicode编码转换为汉字
        result_sign = json.loads(result_signa)
        response_jointask = session.post(url_jointask,cookies=dict_cookies,data=data_jointask,headers=headers_sign,verify=False)
        result_jointask = json.loads(response_jointask.content) #JSON code=200  coins=104  succ=True
        if ( 'code' in result_jointask):
            dd = ("参加10日连续签到成功:" + str(taskcontinue) + '天')
        else:
            dd = ("连续签到进行中:" + str(taskcontinue) + '天')
        
        if  ( 'add_yb_tip' in result_sign):
            result = '用户账号:'+ account + '\n\n签到成功，本次获得' + str(result_sign['add_yb_tip']) + '\n\n已持续签到' + str(result_sign['continue_count']) + '天\n\n' + dd + '\n\n---\n\n'
        else:
            result = '用户账号:'+ account + '\n\n用户已签到\n\n' + dd  + '\n\n---\n\n'
    elif result_login['ret'] == '1':
        retab = '1'
        result = '用户账号:'+ account + '\n\n' + result_login['msg'] + '\n\n---\n\n'
    else :
        retab = '1'
        result = '用户账号:'+ account + '\n\n登陆失败\n\n---\n\n'
    return result,retab