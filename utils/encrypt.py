from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from hashlib import md5
import random
from uuid import uuid1

def AES_Encrypt(data):
    # 正确的密钥和初始化向量
    key = b"u2oh6Vu^HWe4_AES"
    iv = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\x00\x01\x02\x03\x04\x05\x06'  # 正确的IV
    
    # 创建填充器
    padder = padding.PKCS7(128).padder()
    
    # 填充数据
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
    
    # 创建加密器
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # 加密数据
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Base64编码
    return base64.b64encode(encrypted_data).decode('utf-8')
    
def resort(submit_info):
    return {key: submit_info[key] for key in sorted(submit_info.keys())}

def enc(submit_info):
    add = lambda x, y: x + y
    processed_info = resort(submit_info)
    needed = [add(add('[', key), '=' + value) + ']' for key, value in processed_info.items()]
    pattern = "%sd`~7^/>N4!Q#){''"
    needed.append(add('[', pattern) + ']')
    seq = ''.join(needed)
    return md5(seq.encode("utf-8")).hexdigest()


def generate_captcha_key(timestamp: int):
    captcha_key = md5((str(timestamp) + str(uuid1())).encode("utf-8")).hexdigest()
    encoded_timestamp = md5(
        (str(timestamp) + "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1" + "slide" + captcha_key).encode("utf-8")
    ).hexdigest() + ":" + str(int(timestamp) + 0x493e0)
    return [captcha_key, encoded_timestamp]
