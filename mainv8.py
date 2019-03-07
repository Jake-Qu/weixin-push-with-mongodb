#coding=utf-8
from pymongo import MongoClient
import redis
import json
import time
import urllib.request
import urllib.parse
from bson.objectid import ObjectId
from bson.json_util import dumps
import multiprocessing
import logging
import requests
user = 'test'
pwd = 'test'
server = '127.0.0.1'
port = '27017'
db_name = 'test'
uri = 'mongodb://' + user + ':' + pwd + '@' + server + ':' + port + '/' + db_name
connection = MongoClient(uri,connect=True)
db = connection['test']
#定义log
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='push.log',
                    filemode='a')

# 计算今天的unix时间戳
today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
today = time.mktime(time.strptime(today, "%Y-%m-%d"))

#appid = 'wx090939e36d0e6c3a'


def get_appid(touser):
    touser = touser
    value1 = r'''{"openid":"''' + touser + '''"}'''
    value1 = json.loads(value1)
    for result in db.wb_wxuser.find(value1):
        d = dumps(result)
        e = json.loads(d)
        appid = e['appid']
        return(appid)


# 获取access_token
def get_token(touser):
    appid = get_appid(touser)
#    r = redis.Redis(host='172.18.218.118', port='6380')
    r = redis.Redis(connection_pool=redis.ConnectionPool(host='172.18.218.118', port='6380'))
    access_token = r.get('mikkle.wechat.access_token.' + appid)
    r_access_token = access_token.decode('utf-8')
    return (str(r_access_token))

# 获取状态send状态为false并且日期大于今天0点的的document
def get_push_messege():
    dcmt1 = r'''{"inTime":{"$gte":''' + str(today) + '''}}'''
    # dcmt1 = r'''{"inTime":{"$gte":1525231248}}'''
    dcmt2 = r'''{"isSend":false}'''
    document1 = json.loads(dcmt1)
    document2 = json.loads(dcmt2)
    final = {'$and': [document1, document2]}
    count = db.wxpush_test.find(final).count()
    logging.info("the count is " + str(count))
    print("the count is " + str(count))
    for doc in db.wxpush_test.find(final):
        yield (doc)
'''
# post数据方法
def post_data(url, para_dct):
    para_data = para_dct
    req = urllib.request.Request(url, para_data)
    response = urllib.request.urlopen(req)
    content = response.read()
    return content
    logging.info(content)
'''
def post_data(url,para_dct):
    para_data = para_dct
    req = requests.post(url,data=para_data)
    response = req.text
    #print(response)
    return(response)

    ##push数据并返回结果
def do_push_messege(id, touser, template_id, url, data):
    dict_arr = {'touser': touser, 'template_id': template_id, 'url': url, 'data': data}
    json_template = json.dumps(dict_arr, ensure_ascii=False)
    json_template = bytes(json_template, 'utf8')
    token = get_token(touser)
    requst_url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + token
    content = post_data(requst_url, json_template)
    j = json.loads(content)
    j.keys()
    errcode = j['errcode']
    errmsg = j['errmsg']
    count = 0
    while count < 3:
        if errmsg == "ok":
            modify_status(id)
            break
        else:
            content = post_data(requst_url, json_template)
            j = json.loads(content)
            j.keys()
            errmsg = j['errmsg']
        count = count + 1
        print("try count:" + str(count))
    logging.info(str(id) + ":" + errmsg.upper())
    print(errmsg)


def get_json():
    for c in get_push_messege():
        d = dumps(c)
        e = json.loads(d)
        id = e["_id"]
        touser = e["touser"]
        template_id = e["template_id"]
        url = e["url"]
        data = e["data"]
        ##建立一个查找appid的函数
        do_push_messege(id,touser, template_id, url, data)
    # 取每个key的值。然后返回,然后将结果带入do_push_messege(touser,template_id,url,data,color)


def modify_status(id):
    user = 'test'
    pwd = 'test'
    server = '127.0.0.1'
    port = '27017'
    db_name = 'test'
    uri = 'mongodb://' + user + ':' + pwd + '@' + server + ':' + port + '/' + db_name
    connection = MongoClient(uri)
    db = connection['test']
    id.keys()
    r_id = id["$oid"]
    dcmt = {'_id': ObjectId(r_id)}
    db.wxpush_test.find_and_modify(query=dcmt, update={"$set": {'isSend': True}})
    connection.close()

#get_json()

#启用线程池
def main(process_num):
    pool = multiprocessing.Pool(processes=process_num)
    pool.apply_async(get_json())
    pool.close()
    pool.join()
    print("Sub-process(es) done.")

if __name__ == '__main__':

    main(3)

'''
不能用此方法，TCP连接数暴涨
while True:
    main(3)
'''



