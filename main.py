from modules.pipeline import Pipeline
from modules.io_handler import load_instructions, save_output

def simulate_pipeline(instructions):
    pipeline = Pipeline()
    results = []
    # 模擬每條指令
    for instruction in instructions:
        pipeline.step(instruction)
        results.append(f"Cycle {pipeline.cycle}: {instruction}")
        print(f"Cycle {pipeline.cycle}: {instruction}")  # 測試用輸出
    return results

def main():
    # 讀取輸入檔案
    instructions = load_instructions("test6.txt")
    print("Loaded Instructions:", instructions)
    # 執行模擬
    pipeline_results = simulate_pipeline(instructions)
    # 輸出結果
    save_output(pipeline_results, "outputs/result_test6.txt")
    print("Results saved to outputs/result_test6.txt")

if __name__ == "__main__":
    main()
