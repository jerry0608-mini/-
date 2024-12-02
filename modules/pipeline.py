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
        print(f"Cycle {self.cycle + 1}: Fetching instruction: {instruction}")
        return instruction

    def decode(self, instruction):
        """模擬 ID 階段，解析指令"""
        parts = instruction.split()
        op = parts[0]  # 操作碼，例如 lw, sw, add, sub, beq

        if op in ["lw", "sw"]:
            # 使用正則表達式解析寄存器與基址
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', parts[1] + " " + parts[2])
            if match:
                reg = int(match.group(1))   # 目標寄存器號碼，例如 $2 -> 2
                offset = int(match.group(2))  # 偏移值，例如 8
                base = int(match.group(3))    # 基址寄存器號碼，例如 $0 -> 0
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, reg: {reg}, offset: {offset}, base: {base}")
                return {"op": op, "reg": reg, "offset": offset, "base": base}
            else:
                print(f"Invalid instruction format: {instruction}")
                raise ValueError(f"Invalid instruction format: {instruction}")

        elif op in ["add", "sub", "beq"]:
            # 解析 R 型和 I 型指令
            try:
                # 移除寄存器和立即數中的逗號
                rd = int(parts[1].replace(",", "").replace("$", ""))  # 目標寄存器
                rs = int(parts[2].replace(",", "").replace("$", ""))  # 第一操作數寄存器
                rt = int(parts[3].replace(",", "").replace("$", ""))  # 第二操作數寄存器或立即數
                print(f"Cycle {self.cycle + 1}: Decoding instruction: {instruction} -> op: {op}, rd: {rd}, rs: {rs}, rt: {rt}")
                return {"op": op, "rd": rd, "rs": rs, "rt": rt}
            except (ValueError, IndexError) as e:
                print(f"Invalid instruction format: {instruction}")
                raise e

        else:
            # 未知指令
            print(f"Unsupported operation: {op}")
            raise ValueError(f"Unsupported operation: {op}")

    def execute(self, decoded_instruction):
        """模擬 EX 階段"""
        op = decoded_instruction["op"]
        if op == "add":
            result = self.registers[decoded_instruction["rs"]] + self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing ADD -> Result: {result}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"]}
        elif op == "sub":
            result = self.registers[decoded_instruction["rs"]] - self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing SUB -> Result: {result}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"]}
        elif op == "beq":
            taken = self.registers[decoded_instruction["rs"]] == self.registers[decoded_instruction["rt"]]
            print(f"Cycle {self.cycle + 1}: Executing BEQ -> Taken: {taken}")
            return {"op": op, "taken": taken}
        elif op in ["lw", "sw"]:
            address = self.registers[decoded_instruction["base"]] + decoded_instruction["offset"]
            print(f"Cycle {self.cycle + 1}: Executing {op.upper()} -> Address: {address}")
            return {"op": op, "address": address, "reg": decoded_instruction["reg"]}

    def memory_access(self, executed_result, decoded_instruction):
        """模擬 MEM 階段"""
        op = executed_result["op"]
        if op == "lw":
            data = self.memory[executed_result["address"]]
            print(f"Cycle {self.cycle + 1}: Memory Access LW -> Data: {data}")
            return {"op": op, "data": data, "rd": executed_result["reg"]}
        elif op == "sw":
            self.memory[executed_result["address"]] = self.registers[decoded_instruction["reg"]]
            print(f"Cycle {self.cycle + 1}: Memory Access SW -> Memory[{executed_result['address']}] = {self.registers[decoded_instruction['reg']]}")

    def write_back(self, mem_result, decoded_instruction):
        """模擬 WB 階段"""
        if mem_result is None:
            return  # 如果沒有需要寫回的結果，直接返回

        op = mem_result["op"]
        if op in ["lw", "add", "sub"]:
            result = mem_result.get("data", mem_result.get("result"))
            self.registers[mem_result["rd"]] = result
            print(f"Cycle {self.cycle + 1}: Write Back -> Register[{mem_result['rd']}] = {result}")

    def step(self, instruction):
        """模擬一步 Pipeline"""
        # 更新每個 Pipeline 階段
        if self.MEM_WB:
            self.write_back(self.MEM_WB, self.EX_MEM)
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM, self.ID_EX)
        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
        if self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
        self.IF_ID = self.fetch(instruction)
        self.cycle += 1
