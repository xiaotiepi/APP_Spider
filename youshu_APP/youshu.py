'''
有书APP的所有书名爬虫，包括探索新知,提升自我，品质生活，心灵成长，人文社科这5个模块
APP反爬虫措施几乎没有，必须登录才可抓到包，data中的参数不可缺少
APP中一个模块有多种分类，每种分类有多个page，共用一个URL
data中的page参数对应APP中的下拉加载刷新，type参数对用左右滑动选择模块的分类

还有下面这2个模块一定也会完成的（咕咕咕）
早安夜听：https://gongdu.youshu.cc/m/pack/rec_list_simple
近期阅读最多：https://gongdu.youshu.cc/m/page/getIndex?page_id=10010011&page_type=page_1&page=1&limit=20
'''
import requests
import time
from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost:27017/'
client = MongoClient()
db = client['youshu']

# 探索新知,提升自我，品质生活，心灵成长，人文社科这5个模块的链接
urls = ['https://gongdu.youshu.cc/m/page/getIndex?page_id=10010004&page_type=page_5&channel_id=1{}00&type=0&tag_list_id=1&page=1'
        .format(i) for i in range(1, 6)]


def get_start(url):
    '''
    获取和解析模块的信息,生成page和type
    :param url:APP的模块链接
    :return:
    '''
    data = {
        'nonce': '58644',
        'os': 'ios',
        'page': '1',
        'soft': '4.5.4',
        'user_id': '24385915'
    }
    try:
        response = requests.post(url=url, data=data)
        if response.status_code == 200:
            text = response.json()
            datas = text.get('data').get('pageInfo').get('tabsInfo').get('tabs')
            # 生成书类，根据书类再生成页数
            for index, data in enumerate(datas):
                if data.get('title') != '全部':
                    type_num = data.get('type')
                    time.sleep(1)
                    # 生成翻页的页数，不同类型的书，拥有的页数不同，保守点就设个1-99吧
                    for page in range(1, 100):
                        get_page(url, page, type_num)
                        time.sleep(1)  # 降低封号几率
        else:
            print('请求失败,错误代码：', response.status_code)
    except Exception as e:
        print('连接失败：', e)


def get_page(url, page, type_num):
    '''
    获取解析需要的数据
    :param url:APP的模块链接
    :param page:post所需的表单页面参数
    :param type_num:post所需的表单分类参数
    '''
    global db
    data = {
        'nonce': '58644',
        'os': 'ios',
        'page': page,
        'soft': '4.5.4',
        'type': type_num,
        'user_id': '24385915'
    }
    try:
        response = requests.post(url=url, data=data)
        if response.status_code == 200:
            text = response.json()
            datas = text.get('data').get('cards')
            # 提取书本类型
            book_type = text.get('data').get('pageInfo').get('tabsInfo').get('tabs')
            for typE in book_type:
                if typE.get('type') == type_num:
                    book_type = typE.get('title')
                    # 书本类型命名为集合名
                    collection = db[book_type]
            # 提取数据和存储到MongoDB
            if datas:
                for index, data in enumerate(datas):
                    books = data.get('items')
                    for book in books:
                        if book.get('title') not in ['阅读最多', '最新上架']:
                            book_dict = {
                                'book_type': book_type,
                                'book_name': book.get('title'),
                                'book_img': book.get('image')
                            }
                            if collection.insert(book_dict):
                                print(book_dict)
        else:
            print('请求失败,错误代码：', response.status_code)
    except Exception as e:
        print('连接失败：', e)


if __name__ == "__main__":
    for url in urls:
        get_start(url)