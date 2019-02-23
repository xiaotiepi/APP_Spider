'''
剑网三江湖daily的APP爬虫
爬取内容为竞技场前200的个人排名
'''
import time
import requests
import pandas as pd

headers = {
    'Host': 'm.pvp.xoyo.com',
    'Accept': 'application/json',
    'token': '00bd8fe83bce4c98bad26dab4272983c:qsc748:Sv+YX6Zz/EXsb+w/0e/KPg==',
    'Cache-Control': 'no-cache',
    'User-Agent': 'SeasunGame/13 CFNetwork/976 Darwin/18.2.0',
    'Connection': 'keep-alive',
    'Cookie': 'OZ_1U_751=vid=vc34e2c2b69e02.0&ctime=1549294586&ltime=1549294583'
    }

url = 'https://m.pvp.xoyo.com/3c/mine/arena/top200'


def get_page(url, headers):
    '''
    获取json页面
    :param url:请求地址
    :param headers:请求头
    :return:json对象
    '''
    try:
        response = requests.post(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print('请求失败,错误代码：', response.status_code)
    except Exception as e:
        print('连接失败：', e)


def parse_page(result):
    '''
    提取信息,存储为xlsx文件
    :param result:json对象
    :return:
    '''
    datas = result.get('data')
    ranks = []
    for data in datas:
        rank = {}
        rank['门派'] = data.get('personInfo').get('force')
        rank['排名'] = data.get('rankNum')
        rank['胜率'] = data.get('winRate')
        rank['服务器'] = data.get('personInfo').get('zone') + '-' + data.get('personInfo').get('server')
        rank['评分'] = data.get('score')
        rank['名字'] = data.get('personInfo').get('roleName')
        rank['对比上周'] = '0' if data.get('upNum') == '' else data.get('upNum')
        ranks.append(rank)
    t = time.strftime('%Y-%m-%d', time.localtime())
    df = pd.DataFrame(ranks)
    print(df)
    df.to_excel('{}前200排名.xlsx'.format(t), sheet_name=t)


if __name__ == "__main__":
    result = get_page(url, headers)
    parse_page(result)
