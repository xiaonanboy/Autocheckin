# -*- coding: utf-8 -*-
import configparser
import time
import requests
import random
import re
import os
import json
import smzdm
import lenovoclub
import mlenovoclub
import ecloud

#联想签到cookies含有特殊符号"，需替换后json方可loads
def doReplace():
    global path
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(path + '/config.json', mode='r' ,encoding='utf-8') as f_oldfile:
            f_newfile = open(path + '/config_bak.json', 'w', encoding='utf-8')
            for line in f_oldfile :
                if 'cerpreg-passport="' in line :
                    line = re.sub(r'cerpreg-passport="','cerpreg-passport=\\"',line)
                    line = re.sub(r'==\|"','==|\\"',line)
                f_newfile.write(line)
            f_oldfile.close()
            f_newfile.close()
    except IOError :
        print ('config.json不存在')

#配置多账户
def loadConfig(website):
    doReplace()
    try:
        with open(path + '/config_bak.json', 'r', encoding='utf-8') as f:
            dict_config= json.loads(f.read())
            global sckey #获取sckey，定义severchan通道sckey为全局变量，以便pushwechat调用
            sckey = dict_config['SEVERCHAN']
            cookies_list = dict_config[website]
            i = 0
            datalist = []
            for item in cookies_list:
                i += 1
                try:
                    cookies = item['cookies']
                except KeyError as e:
                    print('第%d个账户实例配置出错，跳过该账户' % i, e)
                    continue
                if website == "LENOVOCLUB":
                    mlenovoclub_account = item['account']
                    mlenovoclub_password = item['password']
                    result_mlenovo = mlenovoclub.checkin(mlenovoclub_account,mlenovoclub_password)[0]
                    if mlenovoclub.checkin(mlenovoclub_account,mlenovoclub_password)[1] == '1' :
                        lenovoclub_acc = item['account']
                        result_lenovo = lenovoclub.checkin(cookies,lenovoclub_acc)
                        datalist.append(lenovoclub_acc + "\n\n账号密码登陆失败，尝试使用cookie登录\n\n***联想社区Cookie版***\n\n" + str(result_lenovo))
                    else :
                        datalist.append("***联想社区账号版***\n\n" + str(result_mlenovo))
                elif website == "SMZDM":
                    result_smzdm = smzdm.checkin(cookies)
                    datalist.append("***什么值得买***\n\n" + str(result_smzdm))
                elif website == "HUAWEICLUB":
                    result_huaweiclub = huaweiclub.checkin(cookies)
                    datalist.append(result_huaweiclub)
                elif website == "ECLOUD" :
                    ecloud_signature = item['signature']
                    ecloud_sessionKey = item['sessionKey']
                    result_ecloud = ecloud.checkin(cookies,ecloud_signature,ecloud_sessionKey)
                    datalist.append("***天翼云盘***\n\n" + str(result_ecloud))
                else :
                    print ("other")
            return (datalist)
    except ValueError as e:
        print ('config.json载入错误', e)
    except json.JSONDecodeError as e:
        print('config.json格式有误', e)

def pushWechat(desp):
    send_url='https://sc.ftqq.com/' + sckey + '.send'
    params = {
        'text': '签到提醒'+ time.strftime('%Y-%m-%d %H:%M:%S'),
        'desp': desp
    }
    requests.post(send_url,params=params)

if __name__ == "__main__":
    desp_lenovoclub = loadConfig('LENOVOCLUB')
    desp_smzdz = loadConfig('SMZDM')
    #loadConfig('HUAWEICLUB')
    desp_ecloud = loadConfig('ECLOUD')
    desp = ''.join(desp_lenovoclub) + ''.join(desp_smzdz) + ''.join(desp_ecloud)
    pushWechat(desp)