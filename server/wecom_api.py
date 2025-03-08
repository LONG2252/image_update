import json
import requests
import os
import logging

logger = logging.getLogger(__name__)

headers = {
    "Content-Type":"application/json"
}
wecom_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=*******'
def wecom_function(message):
    try:
        data_new_dict = json.dumps(message)
        response = requests.post(wecom_url, headers=headers,data=data_new_dict )
        return [1,"发送成功"]
    except Exception as e:
        return [0,str(e)]

# data=['测试数据，请无视', '5501679299', 1, 2, [['OP1620', 10, 9, 0]]]
# sa = wecom_function(data)
# print(sa)

