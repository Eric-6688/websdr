import multiprocessing
import os
import time

import requests
from loguru import logger
from requests import RequestException
import execjs
import pandas as pd

# pyinstaller --noconfirm spider.py

@logger.catch()
def get_html(url):
    logger.debug('----开始执行get_html----')
    try:
        # proxies = {
        #     "http": "http://10.10.1.10:3128",
        #     "https": "http://10.10.1.10:1080",
        # }
        # response = requests.get(url, proxies=proxies)
        logger.debug('执行try')
        response = requests.get(url)

        if response.status_code == 200:
            html = response.text
            # html = html.encode('ISO-8859-1')
            # html = html.decode('utf-8')
            logger.debug('----执行get_html完毕----')
            return html
        else:
            logger.debug('网络连接故障')
            return None
    except RequestException:
        print(RequestException)
        return None


def main():
    logger.add(os.getcwd() + '\\log\\{time}.log', encoding="utf-8", rotation="00:00", retention='1 days')
    logger.debug('--------------开始执行main------------------')

    websdr_list = 'http://websdr.ewi.utwente.nl/~~websdrlistk?v=1&chseq=0'
    data_js = get_html(websdr_list)
    # 通过compile命令转成一个js对象
    docjs = execjs.compile(data_js)
    # 调用变量
    res = docjs.eval('sdrs')
    print(res)

    # if os.path.exists('data.js'):
    #     f = open('data.js', 'r')
    #     raw_data = f.read()
    #     docjs = execjs.compile(raw_data)
    #     # # 调用变量
    #     res = docjs.eval('sdrs')
    #     f.close()

    # # 读取js文件
    # with open('data.js', encoding='utf-8') as f:
    #     js = f.read()
    # # 通过compile命令转成一个js对象
    # docjs = execjs.compile(js)
    # # 调用function
    # # res = docjs.call('createGuid')
    # # print(res)
    # # 调用变量
    # res = docjs.eval('sdrs')
    # print(res)

    year = time.strftime('%Y', time.localtime(time.time()))
    month = time.strftime('%m', time.localtime(time.time()))
    day = time.strftime('%d', time.localtime(time.time()))
    hour = time.strftime('%H', time.localtime(time.time()))
    minute = time.strftime('%M', time.localtime(time.time()))
    second = time.strftime('%S', time.localtime(time.time()))

    file_path = os.getcwd() + '\\data\\'
    file_name = year + month + day + hour + minute + second + '.xls'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if os.path.exists(file_path):
        path_name = file_path + '/' + file_name
        logger.debug(path_name)



    df = pd.DataFrame()

    for item in res:
        data = {
            'desc': '',
            'Frequency_range': '',
            'Antenna': '',
            'lon': '',
            'lat': '',
            'url': '',
            'users': '',
            'qth': '',
        }
        if item != None:
            data['desc'] = item['desc'] if 'desc' in item else '------'
            # data['lon'] = item['lon'] if 'lon' in item else '------'
            # data['lat'] = item['lat'] if 'lat' in item else '------'
            if 'lon' in item and 'lat' in item:
                data['lat'], data['lon'] = trans_d2dmd(float(item['lon']), float(item['lat']))
            data['url'] = item['url'] if 'url' in item else '------'
            data['users'] = item['users'] if 'users' in item else '------'
            data['qth'] = item['qth'] if 'qth' in item else '------'
            # Frequency_range = item['bands']
            if 'bands' in item:
                for sub_item in item['bands']:
                    Frequency_low = str(sub_item['l']) if 'l' in sub_item else '------'
                    Frequency_high = str(sub_item['h']) if 'h' in sub_item else '------'
                    Antenna = sub_item['a'] if 'a' in sub_item else '------'

                    # Antenna.append(sub_item['a'])
                    data['Frequency_range'] = Frequency_low+' --- '+Frequency_high + '  MHz'
                    data['Antenna'] = Antenna
                    # data = [i, desc, Frequency_low+' --- '+Frequency_high, Antenna, lon, lat, url, users, qth]
                    print(data)
                    df1 = pd.DataFrame(data,index=[0])

                    df = df.append(df1, sort=False)
            else:
                data['Frequency_range'] = '-----'
                data['Antenna'] = '-----'
                # data = [i, desc, '------', '------', lon, lat, url, users, qth]
                # print(data)
                df1 = pd.DataFrame(data,index=[0])

                df = df.append(df1, sort=False)
    df.to_excel(path_name, index=False)
    # print('df')

    os.system("explorer.exe %s"% file_path)

def trans_d2dmd(d_latitude, d_longitude):
    d = int(d_latitude)
    m = int((d_latitude - d) * 60)
    s = int((d_latitude - d - m / 60) * 3600)
    # print(d, m, s)

    d_1 = int(d_longitude)
    m_1 = int((d_longitude - d_1) * 60)
    s_1 = int((d_longitude - d_1 - m_1 / 60) * 3600)

    # 北纬N 南纬S 东经E 西经W
    # 北纬为正数，南纬为负数；
    # 东经为正数，西经为负数
    if d_latitude > float(0) and d_longitude > float(0):  # 北纬东经
        return str(d).zfill(2) + str(m).zfill(2) + str(s).zfill(2) + 'N', \
               str(d_1).zfill(3) + str(m_1).zfill(2) + str(s_1).zfill(2) + 'E'
    if d_latitude > float(0) and d_longitude < float(0):  # 北纬西经
        return str(d).zfill(2) + str(m).zfill(2) + str(s).zfill(2) + 'N', \
               str(abs(d_1)).zfill(3) + str(abs(m_1)).zfill(2) + str(abs(s_1)).zfill(2) + 'W'
    if d_latitude < float(0) and d_longitude > float(0):  # 南纬东经
        return str(abs(d)).zfill(2) + str(abs(m)).zfill(2) + str(abs(s)).zfill(2) + 'S', \
               str(d_1).zfill(3) + str(m_1).zfill(2) + str(s_1).zfill(2) + 'E'
    if d_latitude < float(0) and d_longitude < float(0):  # 南纬西经
        return str(abs(d)).zfill(2) + str(abs(m)).zfill(2) + str(abs(s)).zfill(2) + 'S', \
               str(abs(d_1)).zfill(3) + str(abs(m_1)).zfill(2) + str(abs(s_1)).zfill(2) + 'W'
    if d_latitude == float(0) or d_longitude == float(0):
        return str(d_latitude), str(d_longitude)

def pandas_excel(path,value):
    data = pd.read_csv('./888.text',sep='\t')
    data.to_excel(path,index=False)

if __name__ == '__main__':
    multiprocessing.freeze_support()  # 最近在使用Pyinstaller打包Python程序的时候发现，打包过程正常，但在运行时会出错，表现为进程不断增加至占满电脑CPU死机，经过网上的多番搜索查阅发现是因为程序使用了多进程模式，而在windows上Pyinstaller打包多进程程序需要添加特殊指令。这里是官方github给出的解释：https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing 修改方式比较简单，在 if __name__=='__main__:'下添加一句multiprocessing.freeze_support() 即可。
    main()
