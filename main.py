from modules.io_handler import load_instructions, save_output
from modules.pipeline import Pipeline

def simulate_pipeline(instructions):
    pipeline = Pipeline()
    results = []
    for instruction in instructions:
        pipeline.step(instruction)
        results.append(f"Cycle {pipeline.cycle}: {instruction}")
    return results
    
'''   當stall後，後面的也會跟著停1個cycle
def simulate_pipeline(instructions):
    pipeline = Pipeline()
    results = []
    index = 0

    while any([pipeline.IF_ID, pipeline.ID_EX, pipeline.EX_MEM, pipeline.MEM_WB]) or index < len(instructions):
        if not pipeline.detect_hazard_lw_stall() and index < len(instructions):
            current_instruction = instructions[index]
            index += 1
        else:
            current_instruction = None  # 插入 NOP
        pipeline.step(current_instruction)
    # 記錄結果
        if current_instruction:
           results.append(f"Cycle {pipeline.cycle}: {current_instruction}")
        else:
           results.append(f"Cycle {pipeline.cycle}: (No new instruction)")
    return results
'''    

def main():
    # 讀取輸入指令檔案
    instructions = load_instructions("inputs/test6.txt")
    print("Loaded Instructions:", instructions)

    # 執行管線模擬
    pipeline_results = simulate_pipeline(instructions)

    # 保存結果到檔案
    save_output(pipeline_results, "outputs/result_test6.txt")
    print("Results saved to outputs/result_test6.txt")

if __name__ == "__main__":
    main()
