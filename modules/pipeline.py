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
