'''
import re
from modules.io_handler import load_instructions

class Pipeline:
    def __init__(self):
        self.IF_ID = None
        self.ID_EX = None
        self.EX_MEM = None
        self.MEM_WB = None

        self.registers = [1] * 32  # 初始化暫存器
        self.registers[0] = 0
        self.memory = [1] * 32

        self.cycle = 0
        self.ForwardA = "00"
        self.ForwardB = "00"

        self.if_taken=0
        self.target_index=0
        self.stall_counter=0
        
        self.simulate_pipeline_index=0
        self.beq_taken_instructions = load_instructions("inputs/test3.txt")

    def fetch(self, instruction):
        self.if_taken=0
        """模擬 IF 階段"""
        if instruction:
            print(f"Cycle {self.cycle + 1}: Fetching instruction: {instruction}")
        return instruction

    def fetch_target(self, target_index):
        """重新抓取目標指令"""
        print(f"Fetching target instruction at index {target_index}")
        # 模擬重新抓取邏輯 (實際指令存取需根據指令存儲結構實作)


    def decode(self, instruction):
        """模擬 ID 階段"""
        if not instruction:
            return None


        parts = instruction.split()
        op = parts[0]
        control_signals = {
            "RegDst": "X", "ALUSrc": "X", "MemtoReg": "X", "RegWrite": "X",
            "MemRead": "X", "MemWrite": "X", "Branch": "X", "ALUOp": "X"
        }

        if op == "beq":
            rs = int(parts[1][1:].replace(",", ""))
            rt = int(parts[2][1:].replace(",", ""))
            offset = int(parts[3])
            control_signals.update({"Branch": "1", "ALUSrc": "0", "ALUOp": "01"})

            print(f"Cycle {self.cycle + 1}: Decoding BEQ -> rs: {rs}, rt: {rt}, offset: {offset}, Signals: {control_signals}")
            return {"op": op, "rs": rs, "rt": rt, "offset": offset, "control": control_signals}

        
        elif op in ["add", "sub"]:
            rd = int(parts[1][1:].replace(",", ""))
            rs = int(parts[2][1:].replace(",", ""))
            rt = int(parts[3][1:].replace(",", ""))
            alu_op = "10" if op == "add" else "11"
            control_signals.update({"RegDst": "1", "ALUSrc": "0", "RegWrite": "1", "ALUOp": alu_op})
            print(f"Cycle {self.cycle + 1}: Decoding {op.upper()} -> rd: {rd}, rs: {rs}, rt: {rt}, Signals: {control_signals}")
            return {"op": op, "rd": rd, "rs": rs, "rt": rt, "control": control_signals}

        elif op in ["lw", "sw"]:
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', " ".join(parts[1:]))
            if match:
                reg = int(match.group(1))
                offset = int(match.group(2))
                base = int(match.group(3))
                control_signals.update({
                    "ALUSrc": "1",
                    "MemRead": "1" if op == "lw" else "0",
                    "MemtoReg": "1" if op == "lw" else "0",
                    "RegWrite": "1" if op == "lw" else "0",
                    "MemWrite": "1" if op == "sw" else "0"
                })
                print(f"Cycle {self.cycle + 1}: Decoding {op.upper()} -> reg: {reg}, offset: {offset}, base: {base}, Signals: {control_signals}")
                return {"op": op, "reg": reg, "offset": offset, "base": base, "control": control_signals}

        raise ValueError(f"Unsupported instruction: {instruction}")

    def execute(self, decoded_instruction):
        """模擬 EX 階段"""
        if not decoded_instruction:
            return None

        op = decoded_instruction["op"]
        control = decoded_instruction["control"]
        self.detect_forwarding_signals(decoded_instruction)
        self.if_taken=0

        if op == "add":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            result = rs_value + rt_value
            print(f"Cycle {self.cycle + 1}: Executing ADD -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}

        elif op == "sub":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            result = rs_value - rt_value
            print(f"Cycle {self.cycle + 1}: Executing SUB -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}
        
        elif op == "beq":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            taken = rs_value == rt_value

            if taken:
                print(f"Cycle {self.cycle + 1}: BEQ Taken -> Flushing pipeline and fetching target")
                # 清空 IF/ID 寄存器 (flush pipeline)
                self.IF_ID = None

                self.target_index=decoded_instruction["offset"]
                print(self.target_index,"*****************測試用*********************")

                if self.target_index!=0:
                   print(f"Fetching target instruction at index {self.simulate_pipeline_index}:")
                   self.IF_ID = self.fetch(self.beq_taken_instructions[self.simulate_pipeline_index+self.target_index-2])
                   self.simulate_pipeline_index=self.simulate_pipeline_index+self.target_index-1

            else:
                print(f"Cycle {self.cycle + 1}: BEQ Not Taken -> Continuing pipeline")
                self.target_index=0

            return {"op": op, "taken": taken, "control": control}

        elif op in ["lw", "sw"]:
            address = self.registers[decoded_instruction["base"]] +  (decoded_instruction["offset"]//4)
            print(f"Cycle {self.cycle + 1}: Executing {op.upper()} -> Address: {address}, Control Signals: {control}")
            return {"op": op, "address": address, "reg": decoded_instruction.get("reg"), "control": control}
        
    def memory_access(self, executed_result):
        """模擬 MEM 階段"""
        if not executed_result:
            return None

        op = executed_result["op"]
        control = executed_result["control"]

        if op == "lw":
            data = self.memory[executed_result["address"]]
            print(f"Cycle {self.cycle + 1}: Memory Access LW -> Data: {data}, Control Signals: {control}")
            return {"op": op, "data": data, "rd": executed_result["reg"], "control": control}
        
        elif op == "sw":
            self.memory[executed_result["address"]] = self.registers[executed_result["reg"]]
            print(f"Cycle {self.cycle + 1}: Memory Access SW -> Memory[{executed_result['address']}] = {self.registers[executed_result['reg']]}, Control Signals: {control}")
            return {"op": op, "control": control}
        
        
        elif op in ["add", "sub"]:
        # 這些指令不需要訪問記憶體，所以直接返回計算的結果
            print(f"Cycle {self.cycle + 1}: Memory Access {op.upper()} -> No memory access needed, Control Signals: {control}")
            return {"op": op, "result": executed_result["result"], "rd": executed_result["rd"], "control": control}
        
        elif op in ["beq"]:
        # 這些指令不需要訪問記憶體，所以直接返回計算的結果
            print(f"Cycle {self.cycle + 1}: Memory Access {op.upper()} -> No memory access needed, Control Signals: {control}")
            return {"op": op,"control": control}
        
    def write_back(self, mem_result):
        """模擬 WB 階段"""
        if not mem_result:
            return

        op = mem_result["op"]
        control = mem_result["control"]
        if op in ["lw", "add", "sub"]:
            result = mem_result.get("data", mem_result.get("result"))
            self.registers[mem_result["rd"]] = result
            print(f"Cycle {self.cycle + 1}: Write Back -> Register[{mem_result['rd']}] = {result}, Control Signals: {control}")
        else:
            print(f"Cycle {self.cycle + 1}: Write Back -> No Register Write, Control Signals: {control}")

    def get_forwarded_value(self, path, reg_index):
        """根據 Forward 信號獲取暫存器值"""
        if path == "A":
            if self.ForwardA == "10":
                return self.EX_MEM["result"]
            elif self.ForwardA == "01":
                return self.MEM_WB["result"]
        elif path == "B":
            if self.ForwardB == "10":
                return self.EX_MEM["result"]
            elif self.ForwardB == "01":
                return self.MEM_WB["result"]
        return self.registers[reg_index]

    def detect_forwarding_signals(self, decoded_instruction):
        """檢測 Forwarding 信號"""
        self.ForwardA = "00"
        self.ForwardB = "00"

        # EX Hazard
        if self.EX_MEM and self.EX_MEM.get("rd") == decoded_instruction.get("rs"):
            self.ForwardA = "10"
        if self.EX_MEM and self.EX_MEM.get("rd") == decoded_instruction.get("rt"):
            self.ForwardB = "10"

        # MEM Hazard
        if self.MEM_WB and self.MEM_WB.get("rd") == decoded_instruction.get("rs") and self.ForwardA != "10":
            self.ForwardA = "01"
        if self.MEM_WB and self.MEM_WB.get("rd") == decoded_instruction.get("rt") and self.ForwardB != "10":
            self.ForwardB = "01"

        # SW Forwarding
        if decoded_instruction["op"] == "sw":
            if self.EX_MEM and self.EX_MEM.get("rd") == decoded_instruction.get("reg"):
                self.ForwardB = "10"
            if self.MEM_WB and self.MEM_WB.get("rd") == decoded_instruction.get("reg") and self.ForwardB != "10":
                self.ForwardB = "01"

    def detect_hazard_lw_stall(self):
        """檢測lw的datahazard"""
        """前一個是lw"""
        if self.ID_EX and self.ID_EX["op"] == "lw":
           rd = self.ID_EX["reg"] 
           if self.IF_ID:
              instr = self.IF_ID.split()
              if instr[0] in ["add", "sub"]:
                 rs = int(instr[2].replace(",", "").replace("$", ""))
                 rt = int(instr[3].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for lw $r{rd}")
                    return True
                 
              elif instr[0] in ["beq"]:
                 rs = int(instr[1].replace(",", "").replace("$", ""))
                 rt = int(instr[2].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for lw $r{rd}")
                    return True 
                 
        #beq前兩個是lw
        elif self.EX_MEM and self.EX_MEM["op"] == "lw":
           rd = self.EX_MEM["reg"] 
           if self.IF_ID:
              instr = self.IF_ID.split()     
              if instr[0] in ["beq"]:
                 rs = int(instr[1].replace(",", "").replace("$", ""))
                 rt = int(instr[2].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for lw $r{rd}")
                    return True   

        #beq前一個是add       
        elif self.ID_EX and self.ID_EX["op"] == "add":
           rd = self.ID_EX["rd"] 
           if self.IF_ID:
              instr = self.IF_ID.split()      
              if instr[0] in ["beq"]:
                 rs = int(instr[1].replace(",", "").replace("$", ""))
                 rt = int(instr[2].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for add $r{rd}")
                    return True

        #beq前一個是sub        
        elif self.ID_EX and self.ID_EX["op"] == "sub":
           rd = self.ID_EX["rd"] 
           if self.IF_ID:
              instr = self.IF_ID.split()      
              if instr[0] in ["beq"]:
                 rs = int(instr[1].replace(",", "").replace("$", ""))
                 rt = int(instr[2].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for sub $r{rd}")
                    return True  
                 
        return False

    def step(self, instruction):
        """模擬一步 Pipeline，處理數據冒險和停滯"""
        output = []  # 用來記錄每個 cycle 的輸出

        if not (self.IF_ID or self.ID_EX or self.EX_MEM or self.MEM_WB or instruction):
           return False
        # 檢測Forwarding
    # 插入stall

        if self.detect_hazard_lw_stall():
            if self.MEM_WB:
               self.write_back(self.MEM_WB)
               output.append(f"{self.MEM_WB['op']}: WB {self.MEM_WB['control']['RegWrite']}")
               self.MEM_WB = None

            if self.EX_MEM:
               self.MEM_WB = self.memory_access(self.EX_MEM)
               control = f"{self.EX_MEM['control']['MemRead']}{self.EX_MEM['control']['MemWrite']}"
               output.append(f"{self.EX_MEM['op']}: MEM {control}")
               self.EX_MEM = None

            if self.ID_EX:
               self.EX_MEM = self.execute(self.ID_EX)
               alu_signals = f"{self.ID_EX['control']['ALUOp']} {self.ID_EX['control']['RegDst']} {self.ID_EX['control']['RegWrite']}"
               output.append(f"{self.ID_EX['op']}: EX {alu_signals}")
               self.ID_EX = None

            if self.IF_ID:
               output.append(f"{self.IF_ID.split()[0]}: ID ")
               self.stall_counter+=1

            self.ID_EX = None
            print(f"Cycle {self.cycle + 1}: Stalling pipeline")

        else: 
            if self.MEM_WB:
               self.write_back(self.MEM_WB)
               self.write_back(self.MEM_WB)
               output.append(f"{self.MEM_WB['op']}: WB {self.MEM_WB['control']['RegWrite']}")
               self.MEM_WB = None
            if self.EX_MEM:
               self.MEM_WB = self.memory_access(self.EX_MEM)
               control = f"{self.EX_MEM['control']['MemRead']}{self.EX_MEM['control']['MemWrite']}"
               output.append(f"{self.EX_MEM['op']}: MEM {control}")
               self.EX_MEM = None
            if self.ID_EX:
               self.EX_MEM = self.execute(self.ID_EX)
               alu_signals = f"{self.ID_EX['control']['ALUOp']} {self.ID_EX['control']['RegDst']} {self.ID_EX['control']['RegWrite']}"
               output.append(f"{self.ID_EX['op']}: EX {alu_signals}")
               self.ID_EX = None

            if self.IF_ID:
               if self.target_index!=0:
                   output.append(f"{self.IF_ID.split()[0]}: IF ")
               else:
                   self.ID_EX = self.decode(self.IF_ID)
                   output.append(f"{self.IF_ID.split()[0]}: ID ")
                   self.IF_ID = None
                   self.stall_counter=0

        # 如果檢測data hazard，Fetch 暫停，不更新 IF/ID
        if instruction and self.target_index==0:
            if self.stall_counter>0:
               output.append(f"{instruction.split()[0]}: IF")
            else:
               self.IF_ID = self.fetch(instruction)
               output.append(f"{instruction.split()[0]}: IF")

        if instruction and self.target_index!=0:
           self.target_index=0
        
        # 更新 Cycle
        self.cycle += 1
        print(f"Cycle {self.cycle}")
        for line in output:
            print(f" {line}")
        print()
        self.print_pipeline_state()


    def print_pipeline_state(self):
        """打印每個 Cycle 中的 Pipeline 狀態，包括控制信號"""
        print(f"Cycle {self.cycle}:")
        print(f"  IF/ID: {self.IF_ID}")
        if self.ID_EX:
            print(f"  ID/EX: {self.ID_EX} | Signals: RegDst={self.ID_EX['control']['RegDst']}, ALUSrc={self.ID_EX['control']['ALUSrc']}, Branch={self.ID_EX['control']['Branch']}, MemRead={self.ID_EX['control']['MemRead']}, MemWrite={self.ID_EX['control']['MemWrite']}, RegWrite={self.ID_EX['control']['RegWrite']}, MemToReg={self.ID_EX['control']['MemtoReg']}")
        else:
            print(f"  ID/EX: {self.ID_EX}")
        if self.EX_MEM:
            print(f"  EX/MEM: {self.EX_MEM} | Signals: ALUResult=X, Zero=X, Branch={self.EX_MEM['control']['Branch']}, MemRead={self.EX_MEM['control']['MemRead']}, MemWrite={self.EX_MEM['control']['MemWrite']}")
        else:
            print(f"  EX/MEM: {self.EX_MEM}")
        if self.MEM_WB:
            print(f"  MEM/WB: {self.MEM_WB} | Signals: RegWrite={self.MEM_WB['control']['RegWrite']}, MemToReg={self.MEM_WB['control']['MemtoReg']}")
        else:
            print(f"  MEM/WB: {self.MEM_WB}")

        if self.ID_EX and self.ID_EX['control']['MemRead'] == '1' and self.ID_EX.get('reg'):
            print("  Pipeline Stalled: Data Hazard Detected")
        elif self.ID_EX and self.ID_EX['op'] == 'beq' and not self.EX_MEM:
            print("  Pipeline Flushed: Control Hazard Detected")
        print()

    def print_final_state(self):
        """打印最終狀態"""
        print("\nFinal Register Values:")
        for i in range(32):
            print(f"$ {i} = {self.registers[i]} ", end="")
        print("\n\nFinal Memory Values:")
        for i in range(32):
            print(f"M[{i}] = {self.memory[i]} ", end="")
        print(f"\n\nTotal Cycles: {self.cycle}")
'''
