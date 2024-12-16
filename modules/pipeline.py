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
        self.predict_taken = False  # 預測是否跳轉，預設為不跳轉

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
            self.predict_taken = False  # 預測 beq 不跳轉
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
            
            # 檢查預測結果是否與實際結果匹配
            if taken != self.predict_taken:
                print(f"Cycle {self.cycle + 1}: Control Hazard Detected: Flushing Pipeline")
                self.IF_ID = None  # 這裡抹掉錯誤的指令
            return {"op": op, "taken": taken, "control": control}

    def step(self, instruction):
        """模擬一步 Pipeline"""
        if self.MEM_WB:
            self.write_back(self.MEM_WB)
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM)

        # 假設要處理控制 Hazard
        if self.IF_ID and self.IF_ID.split()[0] == "beq" and self.EX_MEM and self.EX_MEM.get("taken") == False:
            self.IF_ID = None  # 清空錯誤的指令

        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
        if self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
        self.IF_ID = self.fetch(instruction)

        self.cycle += 1
        self.print_pipeline_state()
