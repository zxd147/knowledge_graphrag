import os
import json


def read_config_file(file_path):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # 打开并读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)  # 解析 JSON 文件
    return config

