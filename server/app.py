#用于更新docker images
#根据本地镜像名称，更新远程镜像名称

import os
from datetime import datetime as dt
from wecom_api import wecom_function

class Update:
    def __init__(self):
        os.system("docker pull frooodle/s-pdf:latest")
        os.system("docker pull evil0ctal/douyin_tiktok_download_api:latest")
        self.dc_name_url = 'registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/'
        self.dc_name_list = ['frooodle/s-pdf:latest','evil0ctal/douyin_tiktok_download_api:latest']
    def image_relationship(self):
        # 定义两个字典，分别存储本地镜像名称和远程镜像名称
        # 其中，data_dict_1表示本地镜像名称和远程镜像名称的映射关系，data_dict_2表示本地镜像名称和
        # 远程镜像名称的映射关系
        data_dict_1 = {
            "online_name":"frooodle/s-pdf:latest",
            "local_name":"registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/s-pdf:latest"
        }
        data_dict_2 = {
            "online_name":"evil0ctal/douyin_tiktok_download_api:latest",
            "local_name":"registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/video_download:latest"
        }
        return [data_dict_1,data_dict_2]

    def main(self):
        try:
            image_dict_list = self.image_relationship()
            for row in image_dict_list:
                print(f"{self.get_time()} 开始更新：{row['online_name']}")

        except Exception as e:
            print(f"{self.get_time()} 程序运行失败：{e}")
    def get_version_info(self):
        images_txt = os.popen("docker images").readlines()
        images_list = []
        image_name = 'registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/s-pdf'
        for row in images_txt[1:]:
            sa_list = row.split()
            if(sa_list and len(sa_list) > 3):
                images_list.append(sa_list)
            else:
                print(f"image:{sa_list},images_length:{len(sa_list)}")
        pdf_local_version=0
        pdf_local_id=0
        local_biggest_version=self.get_biggest_version(images_list)
        for row in images_list: #遍历镜像
            if(row[0]=='frooodle/s-pdf' and row[1]=='latest'): #找到本地镜像，获取最新的id
                pdf_service_id = row[2]
            elif(row[0]==image_name): #找到远程镜像，获取最新的id
                version = self.get_version(row[1]) #获取已上传的最新的版本号
                if(local_biggest_version == version):
                    pdf_local_version = f"{version:.1f}"
                    new_version = f"{(version + 0.1):.1f}"
                    lowwer_version =f"{(version - 0.1):.1f}"
                    pdf_local_id=row[2]
        if(pdf_service_id != pdf_local_id):
            bash_command_list=[]
            bash_command_list.append(f"docker tag {pdf_service_id} {image_name}:v{new_version}")
            bash_command_list.append(f"docker push {image_name}:v{new_version}")
            bash_command_list.append(f"docker rmi {image_name}:v{lowwer_version}") #删除旧版本
            try:
                for row in bash_command_list:
                    os.system(row)
                    print(f"{self.get_time()} 执行命令：{row}")
                message = f"{self.get_time()} {image_name}:v{new_version} 更新成功"
                print(message)
                self.send_wechat(message)
            except Exception as e:
                message = f"{self.get_time()} 执行命令失败：{e}"
                print(message)
        else:
            message = f"{self.get_time()} 服务器镜像：{image_name} 当前id：{pdf_local_id}，版本：v{pdf_local_version}，已是最新，无需更新"
            print(message)
            self.send_wechat(message)

    def get_online_version(self,version):
        try:
            message = f"docker pull registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/s-pdf:v{version} >"
            os.system(message)
        except Exception as e:
            print(f"{self.get_time()} 拉取远程镜像失败：{e}")
    def get_time(self):
        now = dt.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    def get_version(self,v_str):
        if(len(v_str)):
            return float(v_str[1:])
        else:
            return 0
    def get_biggest_version(self,list):
        version_list = []
        for row in list:
            if(row[0]=='registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/s-pdf'):
                version_list.append(self.get_version(row[1]))
        return max(version_list)
    def send_wechat(self,msg):
        try:
            content=f"""##### 镜像更新记录通报
                > 时间: {self.get_time()}
                > 内容: {msg}"""
            send_message = {
              "msgtype": "markdown",
              "markdown": {
                "content": content }
            }
            wecom_function(send_message)
        except Exception as e:
            print(f"{self.get_time()} 发送微信消息失败:{e}")
if __name__ == "__main__":
    Update().main()
