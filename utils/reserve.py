from .encrypt import AES_Encrypt, enc, generate_captcha_key
import json
import requests
import re
import time
import logging
import datetime
import pytz
from urllib3.exceptions import InsecureRequestWarning

class reserve:
    def __init__(self, sleep_time=0.2, max_attempt=50, enable_slider=False, reserve_next_day=False):
        # ... 初始化代码保持不变 ...
    
    def get_target_date(self):
        """获取正确的目标预约日期（北京时间）"""
        now = datetime.datetime.now(self.beijing_tz)
        
        # 简化预约日期计算逻辑
        if self.reserve_next_day:
            # 直接预约明天
            return (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            # 预约今天
            return now.strftime("%Y-%m-%d")
        
    # login and page token
    def _get_page_token(self, url):
        response = self.requests.get(url=url, verify=False)
        html = response.content.decode('utf-8')
        token = re.findall(
            'token: \'(.*?)\'', html)[0] if len(re.findall('token: \'(.*?)\'', html)) > 0 else ""
        return token

    def get_login_status(self):
        """获取登录状态，维持会话 - 添加响应检查"""
        self.requests.headers = self.login_headers
        try:
            response = self.requests.get(url=self.login_page, verify=False)
            if response.status_code == 200:
                logging.info("成功获取登录状态")
                return True
            logging.error(f"获取登录状态失败: HTTP {response.status_code}")
            return False
        except Exception as e:
            logging.error(f"获取登录状态异常: {str(e)}")
            return False

    def login(self, username, password):
        """登录方法 - 添加错误处理"""
        username = AES_Encrypt(username)
        password = AES_Encrypt(password)
        parm = {
            "fid": -1,
            "uname": username,
            "password": password,
            "refer": "http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Fcode%3Fid%3D4219%26seatNum%3D380",
            "t": True
        }
        try:
            response = self.requests.post(url=self.login_url, params=parm, verify=False)
            obj = response.json()
            if obj.get('status', False):
                logging.info(f"用户 {username} 登录成功")
                return True
            else:
                msg = obj.get('msg2', '未知错误')
                logging.error(f"登录失败: {msg}")
                return False
        except Exception as e:
            logging.error(f"登录请求失败: {str(e)}")
            return False

    # ... 其他方法保持不变 ...
