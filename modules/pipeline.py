import re

class Pipeline:
    def __init__(self):
        # Pipeline Buffers
        self.IF_ID = None
        self.ID_EX = None
        self.EX_MEM = None
        self.MEM_WB = None

        # Registers and Memory
        self.registers = [1] * 32  # $0 = 0, others = 1
        self.registers[0] = 0
        self.memory = [1] * 32

        # Cycle counter
        self.cycle = 0

    def fetch(self, instruction):
        """模擬 IF 階段"""
        if instruction:
            print(f"Cycle {self.cycle + 1}: Fetching instruction: {instruction}")
        return instruction

    def decode(self, instruction):
        """模擬 ID 階段，解析指令並設置控制信號"""
        if not instruction:
            return None

        parts = instruction.split()
        op = parts[0]

        control_signals = {
            "RegDst": "X", "ALUSrc": "X", "MemtoReg": "X", "RegWrite": "X",
            "MemRead": "X", "MemWrite": "X", "Branch": "X", "ALUOp": "X"
        }

        if op == "lw":
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', parts[1] + " " + parts[2])
            if match:
                reg = int(match.group(1))
                offset = int(match.group(2))
                base = int(match.group(3))
                # 設置控制信號
                control_signals.update({
                    "RegDst": "0", "ALUSrc": "1", "MemtoReg": "1", "RegWrite": "1",
                    "MemRead": "1", "MemWrite": "0", "Branch": "0", "ALUOp": "00"
                })
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, reg: {reg}, offset: {offset}, base: {base}")
                return {"op": op, "reg": reg, "offset": offset, "base": base, "control": control_signals}
            else:
                print(f"Invalid instruction format: {instruction}")
                raise ValueError(f"Invalid instruction format: {instruction}")

        elif op == "sw":
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', parts[1] + " " + parts[2])
            if match:
                reg = int(match.group(1))
                offset = int(match.group(2))
                base = int(match.group(3))
                # 設置控制信號
                control_signals.update({
                    "RegDst": "X", "ALUSrc": "1", "MemtoReg": "X", "RegWrite": "0",
                    "MemRead": "0", "MemWrite": "1", "Branch": "0", "ALUOp": "00"
                })
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, reg: {reg}, offset: {offset}, base: {base}")
                return {"op": op, "reg": reg, "offset": offset, "base": base, "control": control_signals}
            else:
                print(f"Invalid instruction format: {instruction}")
                raise ValueError(f"Invalid instruction format: {instruction}")

        elif op == "add":
            try:
                rd = int(parts[1].replace(",", "").replace("$", ""))
                rs = int(parts[2].replace(",", "").replace("$", ""))
                rt = int(parts[3].replace(",", "").replace("$", ""))
                # 設置控制信號
                control_signals.update({
                    "RegDst": "1", "ALUSrc": "0", "MemtoReg": "0", "RegWrite": "1",
                    "MemRead": "0", "MemWrite": "0", "Branch": "0", "ALUOp": "10"
                })
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, rd: {rd}, rs: {rs}, rt: {rt}")
                return {"op": op, "rd": rd, "rs": rs, "rt": rt, "control": control_signals}
            except (ValueError, IndexError) as e:
                print(f"Invalid instruction format: {instruction}")
                raise e

        elif op == "beq":
            try:
                rs = int(parts[1].replace(",", "").replace("$", ""))
                rt = int(parts[2].replace(",", "").replace("$", ""))
                offset = int(parts[3].replace(",", "").replace("$", ""))
                # 設置控制信號
                control_signals.update({
                    "RegDst": "X", "ALUSrc": "0", "MemtoReg": "X", "RegWrite": "0",
                    "MemRead": "0", "MemWrite": "0", "Branch": "1", "ALUOp": "01"
                })
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, rs: {rs}, rt: {rt}, offset: {offset}")
                return {"op": op, "rs": rs, "rt": rt, "offset": offset, "control": control_signals}
            except (ValueError, IndexError) as e:
                print(f"Invalid instruction format: {instruction}")
                raise e

        else:
            print(f"Unsupported operation: {op}")
            raise ValueError(f"Unsupported operation: {op}")

    def execute(self, decoded_instruction):
        """模擬 EX 階段"""
        if not decoded_instruction:
            return None

        op = decoded_instruction["op"]
        control = decoded_instruction["control"]
        if op == "add":
            result = self.registers[decoded_instruction["rs"]] + self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing ADD -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}
        elif op == "sub":
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
            return None

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

    def step(self, instruction):
        """模擬一步 Pipeline"""
        # 更新每個 Pipeline 階段，並保持並行
        if self.MEM_WB:
            self.write_back(self.MEM_WB)
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM)
        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
        if self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
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

