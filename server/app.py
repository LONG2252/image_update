#用于更新docker images
#根据本地镜像名称，更新远程镜像名称

import os
import logging
from datetime import datetime as dt
from wecom_api import wecom_function

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('docker_update.log')
    ]
)
logger = logging.getLogger("app_main_program")

class Update:
    def __init__(self):
        os.system("docker pull frooodle/s-pdf:latest >> /dev/null" )
        os.system("docker pull evil0ctal/douyin_tiktok_download_api:latest >> /dev/null")
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
        logger.info("开始运行")
        try:
            image_dict_list = self.image_relationship()
            msg = ""
            for row in image_dict_list:
                update_status,error_msg = self.update_images(row['local_name'],self.get_images_id(row['online_name']))
                if(update_status):
                    delete_count = self.delete_images(row)
                    msg += f"image_name:{row['local_name']} ,image_id:{self.get_images_id(row['online_name'])} 更新成功，删除镜像{delete_count}个!\n"
                else:
                    msg += f"image_name:{row['local_name']} ,image_id:{self.get_images_id(row['online_name'])} 更新失败，报错：{error_msg}\n"
            logger.info(msg)
            self.send_wechat(msg)
        except Exception as e:
            logger.error(f"更新镜像失败，报错：{e}")
    def update_images(self,image_name,image_id):
        bash_command_list=[]
        try:
            bash_command_list.append(f"docker tag {image_id} {image_name}  >> /dev/null")
            bash_command_list.append(f"docker push {image_name} >> /dev/null")
            for row in bash_command_list:
                os.system(row)
            return True,bash_command_list
        except Exception as e:
            error_msg = f"更新镜像:{image_name} 失败，报错：{e}"
            logger.error(error_msg)
            return False,error_msg


    def get_images_id(self,image_name):
        command = "docker images | grep {} | grep latest".format(image_name.split(':')[0])
        images_txt = os.popen(command).readlines()[0]
        return images_txt.split()[2]

    def delete_images(self, image_name_dict):
        image_name_list = []
        image_name_list.append(image_name_dict['online_name'].split(':')[0])
        image_name_list.append(image_name_dict['local_name'].split(':')[0])
        delete_count = 0
        for image_name in image_name_list:
            # 列出所有匹配的镜像
            list_images_command = f"docker images | grep {image_name} | grep -v latest"
            images_txt = os.popen(list_images_command).read()

            # 遍历列出的镜像并删除非latest版本
            for line in images_txt.splitlines():
                if line:
                    # 解析镜像ID和标签
                    parts = line.split()
                    image_id = parts[2]
                    image_tag = parts[-1]

                    # 构建删除命令
                    delete_command = f"docker rmi -f {image_id}  >> /dev/null"
                    try:
                        # 执行删除命令
                        os.system(delete_command)
                        logger.info(f"Deleted image: {image_id}:{image_tag}")
                        delete_count += 1
                    except Exception as e:
                        logger.error(f"删除镜像:{image_id}:{image_tag} 失败，报错：{e}")
        return delete_count
    def send_wechat(self,msg):
        try:
            content=f"""##### 镜像更新记录通报
                > 时间: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}
                > 内容: {msg}"""
            send_message = {
              "msgtype": "markdown",
              "markdown": {
                "content": content }
            }
            wecom_function(send_message)
        except Exception as e:
            logger.error(f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')}发送微信消息失败:{e}")


if __name__ == "__main__":
    Update().main()
