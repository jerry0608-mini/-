from modules.io_handler import load_instructions, save_output
from modules.pipeline import Pipeline

def simulate_pipeline(instructions):
    pipeline = Pipeline(input_number)
    index = 0

    while any([pipeline.IF_ID, pipeline.ID_EX, pipeline.EX_MEM, pipeline.MEM_WB]) or index < len(instructions):
        if pipeline.simulate_pipeline_index!=index:
            index=pipeline.simulate_pipeline_index

        if not pipeline.detect_hazard_lw_stall() and index < len(instructions):
            current_instruction = instructions[index]
            index += 1
            pipeline.simulate_pipeline_index=index
        else:
            if index < len(instructions):
               current_instruction = instructions[index]
            else:
               current_instruction = None
            #current_instruction = None

        pipeline.step(current_instruction)

        # 最終寄存器和記憶體的狀態
    pipeline.output.append("\nFinal Register Values:")
    pipeline.output.append(" ".join([f"${i}={pipeline.registers[i]}" for i in range(32)]))
    pipeline.output.append("\nFinal Memory Values:")
    pipeline.output.append(" ".join([f"M[{i}]={pipeline.memory[i]}" for i in range(32)]))

    # 總執行周期數
    pipeline.output.append(f"\nTotal Cycles: {pipeline.cycle}")
    return pipeline.output

def main():
    # 讀取輸入指令檔案

    instructions = load_instructions("inputs/test"+input_number+".txt")
    print("Loaded Instructions:", instructions)
    # 執行管線模擬
    pipeline_results = simulate_pipeline(instructions)

    # 保存結果到檔案
    save_output(pipeline_results, "outputs/result_test"+input_number+".txt")
    print("Results saved to outputs/result_test"+input_number+".txt")

if __name__ == "__main__":
    input_number=input('請輸入測資號碼')
    pipeline = Pipeline(input_number)
    main()
