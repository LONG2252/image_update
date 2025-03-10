#用于更新docker images
#根据本地镜像名称，拉取远程镜像

import os
import logging
from pathlib import Path
from datetime import datetime as dt
from typing import List, Optional, Union
from dataclasses import dataclass
# from wecom_api import wecom_function



class DockerImageUpdater:
    def __init__(self):
        self.image_name = 'registry.cn-hangzhou.aliyuncs.com/alex_pc_docker/video_download'
        self.yml_file: Path = Path('.docker-compose.yml')

    def update_docker_image(self,image_name):
        """更新docker镜像"""
        try:
            command = f"docker pull {image_name}"
            os.system(command)
            return True
        except Exception as e:
            self.logger.error(f"更新docker镜像失败: {e}")
            return

    def _setup_logging(self) -> None:
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('app')

    def main(self) -> None:
        """主要执行流程"""
        try:
            self._setup_logging()
            if(self.update_docker_image(self.image_name)):
                if(self.restart_local_container()):
                    self.logger.info(f"镜像{self.image_name}更新成功，容器更新成功。")
                    self.del_images(self.image_name)
                else:
                    self.logger.error(f"镜像{self.image_name}更新失败，容器更新失败。")
        except Exception as e:
            self.logger.error(f"程序运行失败: {e}")

    def start_container(self) -> None:
        """更新本地容器"""
        try:
            os.system("cd /data/workspace/image_update/client/video_download && docker-compose up -d --remove-orphans")
            command = f"docker ps | grep {self.image_name}"
            images_txt = os.popen(command).read()
            return True if self.image_name in images_txt else False
        except Exception as e:
            self.logger.error(f"更新本地容器失败: {e}")
            return False

    def restart_local_container(self) -> bool:
        """重启本地容器"""
        try:
            if self.stop_local_container():
                return self.start_container()
            else:
                self.logger.error("停止本地容器失败")
                return False
        except Exception as e:
            self.logger.error(f"重启本地容器失败: {e}")
            return False
            
    def stop_local_container(self) -> bool:
        """停止本地容器"""
        try:
            os.system(f"docker stop $(docker ps -a| grep {self.image_name} | awk '{{print $1}}') && docker rm $(docker ps -a| grep {self.image_name} | awk '{{print $1}}')")
            command = f"docker ps | grep {self.image_name}"
            images_txt = os.popen(command).read()
            return True if self.image_name not in images_txt else False
        except Exception as e:
            self.logger.error(f"停止容器失败: {e}")
            return False
    def del_images(self,image_name):
        try:
            command = f"docker images | grep {image_name} | grep -v latest | awk '{{print $3}}'"
            images_txt_list = os.popen(command).read().split()
            if(len(images_txt_list)):
                try:
                    for row in images_txt_list:
                        new_command = f"docker rmi {row.strip()}"
                        os.system(new_command)
                except Exception as e:
                    self.logger.error(f"删除镜像报错 {e}")
        except Exception as e:
            self.logger.error(f"运行删除镜像任务报错 {e}")

            


    # def create_docker_compose(self, version: str) -> bool:
    #     """创建新的docker-compose配置文件"""
    #     try:
    #         content = self.config.yml_file.read_text()
    #         updated_content = content.replace('latest', f'v{version}')
    #         self.config.yml_cache.write_text(updated_content)
    #         self.logger.info("docker-compose.yml更新完成")
    #         return self.config.yml_cache.exists()
    #     except Exception as e:
    #         self.logger.error(f"docker-compose.yml更新失败: {e}")
    #         return False

    # def get_version_info(self) -> float:
    #     """获取当前版本信息"""
    #     images_txt = os.popen("docker images").readlines()
    #     images_list = [
    #         row.split() for row in images_txt[1:]
    #         if row.split() and len(row.split()) > 3
    #     ]
    #     return self.get_biggest_version(images_list)

    # def get_online_version(self, version: str) -> None:
    #     """获取在线版本"""
    #     try:
    #         command = f"docker pull {self.config.image_name}:v{version}"
    #         os.system(command)
    #         self.logger.info(f"执行拉取命令: {command}")
    #     except Exception as e:
    #         self.logger.error(f"拉取远程镜像失败: {e}")

    # @staticmethod
    # def get_version(v_str: str) -> float:
    #     """解析版本号"""
    #     return float(v_str[1:]) if v_str else 0.0

    # def get_biggest_version(self, image_list: List[List[str]]) -> float:
    #     """获取最大版本号"""
    #     version_list = [
    #         self.get_version(row[1])
    #         for row in image_list
    #         if row[0] == self.config.image_name
    #     ]
    #     return max(version_list) if version_list else 0.0

    def get_time(self):
        now = dt.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    # def send_wechat(self,msg):
    #     try:
    #         content=f"""##### 镜像更新记录通报
    #             > 时间: {self.get_time()}
    #             > 内容: {msg}"""
    #         send_message = {
    #           "msgtype": "markdown",
    #           "markdown": {
    #             "content": content }
    #         }
    #         wecom_function(send_message)
    #     except Exception as e:
    #         print(f"{self.get_time()} 发送微信消息失败:{e}")

if __name__ == "__main__":
    updater = DockerImageUpdater()
    updater.main()
