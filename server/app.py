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
    #更新测试
    def download_images(self,image_name):
        try:
            os.system(f"docker pull {image_name}>> /dev/null" )
            return True
        except Exception as e:
            logger.error(f"download_images 下载镜像:{image_name} 失败，报错：{e}")
            return

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
        data_dict_3= {
            "online_name":"node:latest",
            "local_name":"registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/node:latest"
        }
        return [data_dict_1,data_dict_2,data_dict_3]

    def main(self):
        try:
            image_dict_list = self.image_relationship()
            msg = ""
            logger.info(f"开始更新镜像，共{len(image_dict_list)}个")
            for row in image_dict_list:
                logger.info(f"开始更新镜像:{row['local_name']}")
                if(self.download_images(row['online_name'])):
                    logger.info(f"下载镜像: {row['local_name']} 成功")
                else:
                    logger.error(f"下载镜像: {row['local_name']} 失败")
                    continue
                update_status,error_msg = self.update_images(row['local_name'],self.get_images_id(row['online_name']))
                if(update_status):
                    delete_count = self.delete_images(row)
                    ms = f"镜像更新成功，image_name:{row['local_name']} ,image_id:{self.get_images_id(row['online_name'])} 删除镜像{delete_count}个!"
                    msg += ms + "\n"

                else:
                    ms = f"镜像更新失败，image_name:{row['local_name']} ,image_id:{self.get_images_id(row['online_name'])} ，报错：{error_msg}"
                    msg += ms + "\n"
                logger.info(ms)
            logger.info(msg)
            self.send_wechat(msg)
        except Exception as e:
            logger.error(f"main 更新镜像失败，报错：{e}")
    def update_images(self,image_name,image_id):
        bash_command_list=[]
        try:
            bash_command_list.append(f"docker tag {image_id} {image_name}  >> /dev/null")
            bash_command_list.append(f"docker push {image_name} >> /dev/null")
            for row in bash_command_list:
                os.system(row)
            return True,bash_command_list
        except Exception as e:
            error_msg = f"update_images 更新镜像:{image_name} 失败，报错：{e}"
            logger.error(error_msg)
            return False,error_msg


    def get_images_id(self,image_name):
        try:
            command = f"docker images | grep {(image_name.split(':')[0])} | grep latest"
            images_txt = os.popen(command).readlines()[0]
            return images_txt.split()[2]
        except Exception as e:
            logger.error(f"get_images_id 获取镜像:{image_name} id失败，报错：{e}")


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
            logger.error(f"发送微信消息失败:{e}")


if __name__ == "__main__":
    Update().main()
