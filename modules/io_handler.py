def load_instructions(file_path):
    """讀取指令檔案"""
    with open(file_path, 'r') as file:
        instructions = [line.strip() for line in file.readlines()]
    return instructions

def save_output(results, file_path):
    """將模擬結果存入檔案"""
    with open(file_path, 'w') as file:
        for line in results:
            file.write(line + "\n")
