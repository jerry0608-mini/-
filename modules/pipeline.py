import re

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
        
    def fetch(self, instruction):
        """模擬 IF 階段"""
        if instruction:
            print(f"Cycle {self.cycle + 1}: Fetching instruction: {instruction}")
        return instruction

    def decode(self, instruction):
        """模擬 ID 階段"""
        if not instruction:
            return None

        parts = instruction.split()
        op = parts[0]

        if op == "beq":
            rs = int(parts[1][1:].replace(",", ""))
            rt = int(parts[2][1:].replace(",", ""))
            offset = int(parts[3])
            print(f"Cycle {self.cycle + 1}: Decoding BEQ -> rs: {rs}, rt: {rt}, offset: {offset}")
            return {"op": op, "rs": rs, "rt": rt, "offset": offset}

        elif op in ["add", "sub"]:
            rd = int(parts[1][1:].replace(",", ""))
            rs = int(parts[2][1:].replace(",", ""))
            rt = int(parts[3][1:].replace(",", ""))
            print(f"Cycle {self.cycle + 1}: Decoding {op.upper()} -> rd: {rd}, rs: {rs}, rt: {rt}")
            return {"op": op, "rd": rd, "rs": rs, "rt": rt}

        elif op in ["lw", "sw"]:
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', parts[1] + " " + parts[2])
            if match:
                reg = int(match.group(1))
                offset = int(match.group(2))
                base = int(match.group(3))
                print(f"Cycle {self.cycle + 1}: Decoding {op.upper()} -> reg: {reg}, offset: {offset}, base: {base}")
                return {"op": op, "reg": reg, "offset": offset, "base": base}

        raise ValueError(f"Unsupported instruction: {instruction}")

    def execute(self, decoded_instruction):
        """模擬 EX 階段"""
        if not decoded_instruction:
            return None

        op = decoded_instruction["op"]
        if op == "beq":
            rs_value = self.registers[decoded_instruction["rs"]]
            rt_value = self.registers[decoded_instruction["rt"]]
            taken = rs_value == rt_value
            print(f"Cycle {self.cycle + 1}: Executing BEQ -> Taken: {taken}")
            return {"op": op, "taken": taken}

        elif op == "add":
            result = self.registers[decoded_instruction["rs"]] + self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing ADD -> Result: {result}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"]}

        # 其他指令執行邏輯可類似擴展
        ...

'''forwarding 目前用好add sub
    def execute(self, decoded_instruction):
        """模擬 EX 階段"""
        if not decoded_instruction:
            return None

        op = decoded_instruction["op"]
        control = decoded_instruction["control"]

        # 取得 Forwarding 信號
        ForwardA, ForwardB = self.detect_forwarding_signals()


        if op == "add":
            
            if ForwardA == "00":
               rs_value=self.registers[decoded_instruction["rs"]]
            elif ForwardA == "10":
               rs_value=self.EX_MEM["result"]
            else:
               rs_value=self.MEM_WB["result"]

            if ForwardB == "00":
                rt_value =self.registers[decoded_instruction["rt"]]
            elif ForwardB == "10":
                rt_value=self.EX_MEM["result"]
            else:
                rt_value=self.MEM_WB["result"]

            result = rs_value + rt_value
            print(f"Cycle {self.cycle + 1}: Executing ADD -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}
        
        elif op == "sub":
            if ForwardA == "00":
               rs_value=self.registers[decoded_instruction["rs"]]
            elif ForwardA == "10":
               rs_value=self.EX_MEM["result"]
            else:
               rs_value=self.MEM_WB["data"]

            if ForwardB == "00":
                rt_value =self.registers[decoded_instruction["rt"]]
            elif ForwardB == "10":
                rt_value=self.EX_MEM["result"]
            else:
                rt_value=self.MEM_WB["data"]

            result = rs_value - rt_value
            result = self.registers[decoded_instruction["rs"]] - self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing SUB -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}
        elif op == "beq":
            taken = self.registers[decoded_instruction["rs"]] == self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing BEQ -> Taken: {taken}, Control Signals: {control}")
            return {"op": op, "taken": taken, "control": control}
        elif op in ["lw", "sw"]:
            address = self.registers[decoded_instruction["base"]] + decoded_instruction["offset"]
            print(f"Cycle {self.cycle + 1}: Executing {op.upper()} -> Address: {address}, Control Signals: {control}")
            return {"op": op, "address": address, "reg": decoded_instruction.get("reg"), "control": control}
'''
    
    def memory_access(self, executed_result):
        """模擬 MEM 階段"""
        if not executed_result:
            return None

        # 針對 lw 和 sw 指令處理記憶體訪問
        ...

    def write_back(self, mem_result):
        """模擬 WB 階段"""
        if not mem_result:
            return

        op = mem_result["op"]
        if op in ["lw", "add", "sub"]:
            result = mem_result.get("data", mem_result.get("result"))
            self.registers[mem_result["rd"]] = result
            print(f"Cycle {self.cycle + 1}: Write Back -> Register[{mem_result['rd']}] = {result}")


    def detect_forwarding_signals(self):
        """檢測是否需要 Forwarding 並設置 ForwardA 和 ForwardB """
        ForwardA = "00"  # 預設為00
        ForwardB = "00"

        # EX Hazard
        if self.EX_MEM and self.EX_MEM.get("control", {}).get("RegWrite") == "1":
           if self.EX_MEM.get("rd") == self.ID_EX.get("rs"):
              ForwardA = "10"
           if self.EX_MEM.get("rd") == self.ID_EX.get("rt"):
              ForwardB = "10"

        # MEM Hazard
        if self.MEM_WB and self.MEM_WB.get("control", {}).get("RegWrite") == "1":
           if self.MEM_WB.get("rd") == self.ID_EX.get("rs") and ForwardA != "10":
              ForwardA = "01"
           if self.MEM_WB.get("rd") == self.ID_EX.get("rt") and ForwardB != "10":
              ForwardB = "01"

        return ForwardA, ForwardB
        
    def detect_hazard_lw_stall(self):
        """檢測lw的datahazard"""
        if self.ID_EX and self.ID_EX["op"] == "lw":
           rd = self.ID_EX["reg"] 
           if self.IF_ID:
              instr = self.IF_ID.split()
              if instr[0] in ["add", "sub", "beq"]:
                 rs = int(instr[2].replace(",", "").replace("$", ""))
                 rt = int(instr[3].replace(",", "").replace("$", ""))
                 if rd in [rs, rt]:
                    print(f"Data Hazard detected: Stalling for lw $r{rd}")
                    return True
        return False
        
    def step(self, instruction):
        """模擬一步 Pipeline"""
        if self.MEM_WB:
            self.write_back(self.MEM_WB)
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM)
        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
        if self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
        self.IF_ID = self.fetch(instruction)

        self.cycle += 1

'''解決 Data Hazard 的 stall，forward還沒用好

    def step(self,  instruction):
        """模擬一步 Pipeline"""
        if not (self.IF_ID or self.ID_EX or self.EX_MEM or self.MEM_WB or instruction):
           return False
        
    # 插入stall
        if self.detect_hazard_lw_stall():
            if self.MEM_WB:
               self.write_back(self.MEM_WB)
               self.MEM_WB = None
            if self.EX_MEM:
               self.MEM_WB = self.memory_access(self.EX_MEM)
               self.EX_MEM = None
            if self.ID_EX:
               self.EX_MEM = self.execute(self.ID_EX)
               self.ID_EX = None

            self.ID_EX = None
            print(f"Cycle {self.cycle + 1}: Stalling pipeline")
            
        else: 
            if self.MEM_WB:
               self.write_back(self.MEM_WB)
               self.MEM_WB = None
            if self.EX_MEM:
               self.MEM_WB = self.memory_access(self.EX_MEM)
               self.EX_MEM = None
            if self.ID_EX:
               self.EX_MEM = self.execute(self.ID_EX)
               self.ID_EX = None
            if self.IF_ID:
               self.ID_EX = self.decode(self.IF_ID)
               self.IF_ID = None

        # 如果檢測data hazard，Fetch 暫停，不更新 IF/ID
        if not self.detect_hazard_lw_stall() and instruction:
           self.IF_ID = self.fetch(instruction)

        # 更新 Cycle
        self.cycle += 1
        self.print_pipeline_state()

    def print_pipeline_state(self):
        """打印每個 Cycle 中的 Pipeline 狀態，包括控制信號"""
        print(f"Cycle {self.cycle}:")
        print(f"  IF/ID: {self.IF_ID}")
        print(f"  ID/EX: {self.ID_EX}")
        print(f"  EX/MEM: {self.EX_MEM}")
        print(f"  MEM/WB: {self.MEM_WB}")
        print()
'''
