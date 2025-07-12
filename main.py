import json
import time
import argparse
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from utils import reserve

# 修复：移除未使用的action参数
get_current_time = lambda: time.strftime("%H:%M:%S", time.localtime(time.time() + 8*3600))
get_current_dayofweek = lambda: time.strftime("%A", time.localtime(time.time() + 8*3600))

def wait_until(target_time, action):
    """更严格的等待函数，精确到毫秒级"""
    logging.info(f"严格等待目标时间: {target_time}")
    target_h, target_m, target_s = map(int, target_time.split(':'))
    target_ts = target_h*3600 + target_m*60 + target_s
    
    while True:
        current_time = get_current_time()
        current_h, current_m, current_s = map(int, current_time.split(':'))
        current_ts = current_h*3600 + current_m*60 + current_s
        
        if current_ts >= target_ts:
            logging.info(f"精确达到目标时间: {current_time}")
            break
            
        # 更精确的等待，每秒检查10次
        time.sleep(0.1)

SLEEPTIME = 0.2
ENDTIME = "21:31:00"
ENABLE_SLIDER = True
MAX_ATTEMPT = 1
RESERVE_TOMORROW = True  # 使用正确的变量名

def get_user_credentials(action):
    if action:
        try:
            usernames = os.environ['USERNAMES']
            passwords = os.environ['PASSWORDS']
            return usernames, passwords
        except KeyError:
            logging.error("Missing USERNAMES or PASSWORDS in environment variables")
            return "", ""
    return "", ""

def login_and_reserve(users, usernames, passwords, action, success_list=None):
    # 修复日志输出中的变量名
    logging.info(f"Global settings: \nSLEEPTIME: {SLEEPTIME}\nENDTIME: {ENDTIME}\nENABLE_SLIDER: {ENABLE_SLIDER}\nRESERVE_TOMORROW: {RESERVE_TOMORROW}")
    
    if action and len(usernames.split(",")) != len(users):
        raise Exception("user number should match the number of config")
    if success_list is None:
        total_tasks = sum(len(user["tasks"]) for user in users)
        success_list = [False] * total_tasks
        
    current_dayofweek = get_current_dayofweek()
    session_cache = {}
    task_index = 0
    
    for index, user in enumerate(users):
        username = user["username"]
        password = user["password"]
        
        if action:
            cred_list = usernames.split(',')
            if index < len(cred_list):
                username = cred_list[index]
            else:
                logging.error(f"Not enough usernames in secrets for index {index}")
                continue
            
            cred_list = passwords.split(',')
            if index < len(cred_list):
                password = cred_list[index]
            else:
                logging.error(f"Not enough passwords in secrets for index {index}")
                continue
            
        if username not in session_cache:
            logging.info(f"----------- {username} login -----------")
            s = reserve(sleep_time=SLEEPTIME, max_attempt=MAX_ATTEMPT, 
                        enable_slider=ENABLE_SLIDER, reserve_next_day=RESERVE_TOMORROW)
            
            # 添加登录状态检查
            if not s.get_login_status():
                logging.error("获取登录状态失败，跳过该用户")
                continue
                
            if not s.login(username, password):
                logging.error("登录失败，跳过该用户")
                continue
                
            s.requests.headers.update({'Host': 'office.chaoxing.com'})
            session_cache[username] = s
        else:
            s = session_cache[username]
            
        for task in user["tasks"]:
            times = task["time"]
            roomid = task["roomid"]
            seatid = task["seatid"]
            daysofweek = task["daysofweek"]
            
            if current_dayofweek not in daysofweek:
                logging.info(f"Task {task_index}: Today not set to reserve")
                task_index += 1
                continue
                
            if not success_list[task_index]:
                logging.info(f"----------- {username} -- {times} -- {seatid} try -----------")
                suc = s.submit(times, roomid, seatid, action)
                success_list[task_index] = suc
                
            task_index += 1
            
    return success_list

def main(users, action=False):
    current_time = get_current_time()
    logging.info(f"启动时间 {current_time}, 执行模式 {'开启' if action else '关闭'}")
    attempt_times = 0
    usernames, passwords = None, None
    
    # 在GitHub Actions中运行时
    if action:
        logging.info("检测到GitHub Actions模式，执行精确时间控制")
        
        # 第一步：严格等待到北京时间16:28:00
        logging.info("严格等待到北京时间20:35:00...")
        wait_until("20:35:00", action)
        logging.info("北京时间20:35:00 - 开始登录账号")
        
        # 获取环境变量中的账号密码
        usernames, passwords = get_user_credentials(action)
        
        # 登录账号
        logging.info("开始账号登录流程")
        success_list = login_and_reserve(users, usernames, passwords, action, None)
        logging.info("账号登录完成")
        
        # 第二步：严格等待到北京时间16:29:00
        logging.info("严格等待到北京时间20:36:00...")
        wait_until("20:36:00", action)
        logging.info("北京时间20:36:00 - 开始预约流程")
    
    # 非GitHub Actions模式
    else:
        if action:
            usernames, passwords = get_user_credentials(action)
        else:
            usernames, passwords = "", ""
        success_list = None
        
    # 原有的预约循环
    total_tasks = sum(len(user["tasks"]) for user in users)
    current_time = get_current_time()
    
    while current_time < ENDTIME:
        attempt_times += 1
        success_list = login_and_reserve(users, usernames, passwords, action, success_list)
        logging.info(f"尝试次数 {attempt_times}, 当前时间 {current_time}, 成功列表 {success_list}")
        current_time = get_current_time()
        
        if sum(success_list) == total_tasks:
            logging.info("所有任务预约成功!")
            return
            
    logging.info(f"达到结束时间 {ENDTIME}，停止尝试")

# ... debug和get_roomid函数保持不变 ...
