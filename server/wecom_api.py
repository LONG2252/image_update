import json
import requests
import logging

logger = logging.getLogger("send_to_wechat")

headers = {
    "Content-Type":"application/json"
}
wecom_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=*******'
def wecom_function(message):
    try:
        data_new_dict = json.dumps(message)
        response = requests.post(wecom_url, headers=headers,data=data_new_dict )
        return True,response.text
    except Exception as e:
        return False,str(e)

# data=['测试数据，请无视', '5501679299', 1, 2, [['OP1620', 10, 9, 0]]]
# sa = wecom_function(data)
# print(sa)

