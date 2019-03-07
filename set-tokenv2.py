#两小时执行一次，因为7200秒（2小时）过期
import urllib.request
import urllib.parse
import redis
import json
import logging

#定义log
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='token.log',
                    filemode='a')

#微信号id
appid="your appid"
#测试微信号sc
secret="your secret"
url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+ appid +'&secret='+ secret
def get_data(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    content = response.read()
    j = json.loads(content)
    j.keys()
    try:
        access_token=j["access_token"]
    except Exception as KeyError:
        logging.error("检查你的appid/secret,停止插入Redis，微信返回结果：" + str(content))
        print("检查你的appid/secret,停止插入Redis，微信返回结果：" + str(content))
    else:
        return(access_token)

def set_token():
    access_token= get_data(url)
    if access_token is None:
        exit(1)
    else:
        r = redis.Redis(host='172.18.218.118', port='6380')
        result = r.set('mikkle.wechat.access_token.' + appid, access_token)
        logging.info("set token to redis success!")
        print(result)

if __name__ == '__main__':
    set_token()

