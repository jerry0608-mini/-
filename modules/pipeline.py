
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
        return instruction
def decode(self, instruction):
    """模擬 ID 階段，解析指令"""
    parts = instruction.split()
    op = parts[0]  # 操作碼，例如 lw, sw, add, sub, beq

    if op in ["lw", "sw"]:
        # 確保指令格式正確
        try:
            reg, offset = parts[1].split('(')
            reg = int(reg[1:])  # 去掉 $ 符號，例如 $2 -> 2
            offset = int(offset[:-1])  # 去掉 )
            base = int(parts[2][1:])  # 基址寄存器，例如 $0 -> 0
            return {"op": op, "reg": reg, "offset": offset, "base": base}
        except (ValueError, IndexError) as e:
            print(f"Invalid instruction format: {instruction}")
            raise e

    elif op in ["add", "sub", "beq"]:
        # 解析 R 型和 I 型指令
        try:
            rd = int(parts[1][1:])  # 目標寄存器
            rs = int(parts[2][1:])  # 第一操作數寄存器
            rt = int(parts[3][1:])  # 第二操作數寄存器或立即數
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
            return {"result": self.registers[decoded_instruction["rs"]] + self.registers[decoded_instruction["rt"]]}
        elif op == "sub":
            return {"result": self.registers[decoded_instruction["rs"]] - self.registers[decoded_instruction["rt"]]}
        elif op == "beq":
            return {"taken": self.registers[decoded_instruction["rs"]] == self.registers[decoded_instruction["rt"]]}
        elif op == "lw" or op == "sw":
            return {"address": self.registers[decoded_instruction["base"]] + decoded_instruction["offset"]}

    def memory_access(self, executed_result, decoded_instruction):
        """模擬 MEM 階段"""
        op = decoded_instruction["op"]
        if op == "lw":
            return {"data": self.memory[executed_result["address"]]}
        elif op == "sw":
            self.memory[executed_result["address"]] = self.registers[decoded_instruction["reg"]]

    def write_back(self, mem_result, decoded_instruction):
        """模擬 WB 階段"""
        op = decoded_instruction["op"]
        if op == "lw" or op == "add" or op == "sub":
            self.registers[decoded_instruction["rd"]] = mem_result.get("data", mem_result.get("result"))

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
