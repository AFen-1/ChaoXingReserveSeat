# ... 文件顶部代码保持不变 ...

def wait_until(target_time, action):
    """更严格的等待函数，精确到毫秒级"""
    logging.info(f"严格等待目标时间: {target_time}")
    target_h, target_m, target_s = map(int, target_time.split(':'))
    target_ts = target_h*3600 + target_m*60 + target_s
    
    while True:
        current_time = get_current_time(action)
        current_h, current_m, current_s = map(int, current_time.split(':'))
        current_ts = current_h*3600 + current_m*60 + current_s
        
        if current_ts >= target_ts:
            logging.info(f"精确达到目标时间: {current_time}")
            break
            
        # 更精确的等待，每秒检查10次
        time.sleep(0.1)

def main(users, action=False):
    # ... 前面代码保持不变 ...
    
    if action:
        logging.info("检测到GitHub Actions模式，执行精确时间控制")
        
        # 第一步：严格等待到北京时间21:29:00
        logging.info("严格等待到北京时间21:29:00...")
        wait_until("21:29:00", action)
        logging.info("北京时间21:29:00 - 开始登录账号")
        
        # 获取环境变量中的账号密码
        usernames, passwords = get_user_credentials(action)
        
        # 登录账号
        logging.info("开始账号登录流程")
        success_list = login_and_reserve(users, usernames, passwords, action, None)
        logging.info("账号登录完成")
        
        # 第二步：严格等待到北京时间21:30:00
        logging.info("严格等待到北京时间21:30:00...")
        wait_until("21:30:00", action)
        logging.info("北京时间21:30:00 - 开始预约流程")
    
    # ... 后续代码保持不变 ...
