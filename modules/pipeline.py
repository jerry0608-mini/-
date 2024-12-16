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
            print(f"Cycle {self.cycle + 1}: Executing BEQ -> Taken: {taken}, Control Signals: {control}")
            return {"op": op, "taken": taken, "control": control}

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

    def memory_access(self, executed_result):
        """模擬 MEM 階段"""
        if not executed_result:
            return None

        op = executed_result["op"]
        control = executed_result["control"]
        if op == "lw":
            data = self.memory[executed_result["address"]]
            print(f"Cycle {self.cycle + 1}: Memory Access LW -> Data: {data}, Control Signals: {control}")
            return {"op": op, "data": data, "rd": executed_result["rd"], "control": control}
        elif op == "sw":
            self.memory[executed_result["address"]] = self.registers[executed_result["reg"]]
            print(f"Cycle {self.cycle + 1}: Memory Access SW -> Memory[{executed_result['address']}] = {self.registers[executed_result['reg']]}, Control Signals: {control}")

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

    def step(self, instruction):
        """模擬一步 Pipeline"""
        if self.MEM_WB:
            self.write_back(self.MEM_WB)
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM)

        # LW Data Hazard Detection
        if self.ID_EX and self.ID_EX["op"] == "lw":
            if self.IF_ID:
                parts = self.IF_ID.split()
                if len(parts) > 2:
                    match = re.match(r'(\d+)\(\$(\d+)\)', parts[2])
                    if match:
                        base = int(match.group(2))
                        if self.ID_EX["reg"] == base:
                            print(f"Cycle {self.cycle + 1}: Data Hazard Detected -> Stalling Pipeline")
                            self.EX_MEM = None
                            self.MEM_WB = None
                            return

        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
        if self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
        self.IF_ID = self.fetch(instruction)

        self.cycle += 1
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

        # 增強輸出，處理管線暫停或清空的情況
        if self.ID_EX and self.ID_EX['control']['MemRead'] == '1' and self.ID_EX.get('reg'):
            print("  Pipeline Stalled: Data Hazard Detected")
        elif self.ID_EX and self.ID_EX['op'] == 'beq' and not self.EX_MEM:
            print("  Pipeline Flushed: Control Hazard Detected")
        print()