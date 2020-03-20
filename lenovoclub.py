import requests
import time
import json
import re
import configparser

def checkin(myCookie,acc):
    #acc 用户多账户区分用户
    url_signlist = 'https://club.lenovo.com.cn/signlist'
    url_checkin = 'https://club.lenovo.com.cn/sign'
    url_joinchallenge = 'https://club.lenovo.com.cn/joinchallengetask'
    signlist = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': myCookie,
        'referer': 'https://club.lenovo.com.cn/thread-1814833-1-1.html',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-length': '47',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': myCookie,
        'origin': 'https://club.lenovo.com.cn',
        'referer': 'https://club.lenovo.com.cn/signlist',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    #headersdata=json.dumps(headers)  # 如遇特殊符号（:authority: club.lenovo.com.cn，:scheme: https） 需字典数据转为json，需要使用json.dumps
    session = requests.session()
    response_signlist = session.get(url_signlist,headers=signlist,verify=True)
    token_utf8 = response_signlist.content.decode("utf-8")
    result_token = re.search('CONFIG.token\s=\s"\w{40}',token_utf8) #获取随机token
    myToken = result_token.group()[-40:]
    result_taskcontinue = re.search('class="signInLiBottom">进行中.{1,5}',token_utf8)
    taskcontinue = result_taskcontinue.group()[-5:]

    data = {
        '_token': myToken
    }

    data_joinchallenge = {
        'task_id': '3',
        '_token': myToken
    }
    
    #参加连续签到任务
    response_joinchallenge = session.post(url_joinchallenge,headers=headers,data=data_joinchallenge,verify=True) #{"succ":true,"coins":31578,"code":200}
    result_joinchallenge = json.loads(response_joinchallenge.content)
    global dd
    if ( 'code' in result_joinchallenge):
        dd = ("参加10日连续签到成功" + taskcontinue)
    else:
        dd = ("连续签到进行中" + taskcontinue)

    response = session.post(url_checkin, headers=headers, data=data) #json=headers 转为json解决headers特殊符号':authority': 'club.lenovo.com.cn',':path': '/sign',':scheme': 'https',
    result = response.content.decode("unicode_escape")# unicode编码转换为汉字
    try:
        result_checkin = json.loads(result)
        if result_checkin['code'] == 100000 :
            result0 = '\n\n用户id:'+ acc + '\n\n' + '签到成功，本次获得' + str(result_checkin['data']['data']['add_yb_tip']) + '\n\n' + '已持续签到' + str(result_checkin['data']['signCal']['continue_count']) + '天' + '\n\n' + '已累计获得延保' + str(result_checkin['data']['signCal']['user_yanbao_score']) + '天\n\n' + dd + '\n\n---\n\n'
        elif result_checkin['code'] == 100001 :
            result0 = '\n\n用户id:'+ acc + '\n\n' + str(result_checkin['msg'] + '\n\n' + dd + '\n\n---\n\n')
        else:
            result0 = '签到失败\n\n---\n\n'
    except ValueError:
        result0 = '网页打开失败，非json(cookie失效)\n\n---\n\n'
    return result0