import os

def load_instructions(file_path):
    """讀取指令檔案"""
    with open(file_path, 'r') as file:
        instructions = [line.strip() for line in file.readlines()]
    return instructions

def save_output(results, file_path):
    """將模擬結果存入檔案"""
    # 確保目錄存在
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 保存結果到檔案
    with open(file_path, 'w') as file:
        for line in results:
            file.write(line + "\n")
