import re

class Pipeline:
    def __init__(self):
        # 五級流水線暫存器
        self.IF_ID = None
        self.ID_EX = None
        self.EX_MEM = None
        self.MEM_WB = None

        # 初始化暫存器與記憶體 (32 個)
        self.registers = [1] * 32
        self.registers[0] = 0  # $0 恒為 0
        self.memory = [1] * 32

        # 其餘紀錄
        self.cycle = 0
        self.ForwardA = "00"
        self.ForwardB = "00"
    
    ## --------------------- IF 階段 --------------------- ##
    def fetch(self, instruction):
        """模擬 IF 階段 (取指)"""
        if instruction:
            # **移除多餘的 "Cycle {self.cycle + 1}:"，只印簡短提示**
            print(f"[IF] Fetching instruction: {instruction}")
        return instruction

    def fetch_target(self, target_index):
        """重新抓取目標指令 (此處僅示範印出)"""
        # 同樣移除多餘的 cycle prefix，只印提示
        print(f"[IF] Fetching target instruction at index {target_index}")
        # 真正完整做法應維護 PC / 指令記憶體，這裡僅示範

    ## --------------------- ID 階段 --------------------- ##
    def decode(self, instruction):
        """模擬 ID 階段 (譯碼)"""
        if not instruction:
            return None

        parts = instruction.split()
        op = parts[0]
        # 預設控制訊號皆為 X
        control_signals = {
            "RegDst": "X", "ALUSrc": "X", "MemtoReg": "X", "RegWrite": "X",
            "MemRead": "X", "MemWrite": "X", "Branch": "X", "ALUOp": "X"
        }

        # 判斷指令類型 (R-type, lw, sw, beq)
        if op == "beq":
            rs = int(parts[1][1:].replace(",", ""))
            rt = int(parts[2][1:].replace(",", ""))
            offset = int(parts[3])
            control_signals.update({"Branch": "1", "ALUSrc": "0", "ALUOp": "01"})
            # 移除多餘的 cycle prefix
            print(f"[ID] Decoding BEQ -> rs: {rs}, rt: {rt}, offset: {offset}, Signals: {control_signals}")
            return {"op": op, "rs": rs, "rt": rt, "offset": offset, "control": control_signals}

        elif op in ["add", "sub"]:
            rd = int(parts[1][1:].replace(",", ""))
            rs = int(parts[2][1:].replace(",", ""))
            rt = int(parts[3][1:].replace(",", ""))
            alu_op = "10" if op == "add" else "11"
            control_signals.update({
                "RegDst": "1", "ALUSrc": "0", 
                "RegWrite": "1", 
                "ALUOp": alu_op
            })
            print(f"[ID] Decoding {op.upper()} -> rd: {rd}, rs: {rs}, rt: {rt}, Signals: {control_signals}")
            return {"op": op, "rd": rd, "rs": rs, "rt": rt, "control": control_signals}

        elif op in ["lw", "sw"]:
            # 指令格式: lw $X, imm($Y) 或 sw $X, imm($Y)
            match = re.match(r'\$(\d+),\s*(\d+)\(\$(\d+)\)', " ".join(parts[1:]))
            if match:
                reg = int(match.group(1))
                offset = int(match.group(2))
                base = int(match.group(3))
                # lw 與 sw 的控制訊號設定
                if op == "lw":
                    control_signals.update({
                        "ALUSrc": "1", "MemRead": "1", "MemtoReg": "1",
                        "RegWrite": "1", "MemWrite": "0"
                    })
                else:  # sw
                    control_signals.update({
                        "ALUSrc": "1", "MemRead": "0", "MemtoReg": "0",
                        "RegWrite": "0", "MemWrite": "1"
                    })
                print(f"[ID] Decoding {op.upper()} -> reg: {reg}, offset: {offset}, base: {base}, Signals: {control_signals}")
                return {"op": op, "reg": reg, "offset": offset, "base": base, "control": control_signals}

        raise ValueError(f"Unsupported instruction: {instruction}")

    ## --------------------- EX 階段 --------------------- ##
    def execute(self, decoded_instruction):
        """模擬 EX 階段 (執行)"""
        if not decoded_instruction:
            return None

        op = decoded_instruction["op"]
        control = decoded_instruction["control"]
        # 檢查並設定 Forwarding
        self.detect_forwarding_signals(decoded_instruction)

        if op == "add":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            result = rs_value + rt_value
            print(f"[EX] Executing ADD -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}

        elif op == "sub":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            result = rs_value - rt_value
            print(f"[EX] Executing SUB -> Result: {result}, Control Signals: {control}")
            return {"op": op, "result": result, "rd": decoded_instruction["rd"], "control": control}

        elif op == "beq":
            rs_value = self.get_forwarded_value("A", decoded_instruction["rs"])
            rt_value = self.get_forwarded_value("B", decoded_instruction["rt"])
            taken = (rs_value == rt_value)

            if taken:
                # 如果 branch 成立，flush pipeline + 重新抓取
                print("[EX] BEQ Taken -> Flushing pipeline and fetching target")
                self.IF_ID = None
                # 計算目標，這裡僅示範印出
                target_index = self.cycle + decoded_instruction["offset"]
                self.fetch_target(target_index)
            else:
                print("[EX] BEQ Not Taken -> Continuing pipeline")

            return {"op": op, "taken": taken, "control": control}

        elif op in ["lw", "sw"]:
            address = self.registers[decoded_instruction["base"]] + decoded_instruction["offset"]
            print(f"[EX] Executing {op.upper()} -> Address: {address}, Control Signals: {control}")
            return {"op": op, "address": address, "reg": decoded_instruction.get("reg"), "control": control}

    ## --------------------- MEM 階段 --------------------- ##
    def memory_access(self, executed_result):
        """模擬 MEM 階段 (存取記憶體)"""
        if not executed_result:
            return None

        op = executed_result["op"]
        control = executed_result["control"]

        if op == "lw":
            data = self.memory[executed_result["address"]]
            print(f"[MEM] LW -> Read Data: {data}, Control Signals: {control}")
            return {"op": op, "data": data, "rd": executed_result["reg"], "control": control}

        elif op == "sw":
            self.memory[executed_result["address"]] = self.registers[executed_result["reg"]]
            stored_val = self.registers[executed_result["reg"]]
            print(f"[MEM] SW -> Memory[{executed_result['address']}] = {stored_val}, Control Signals: {control}")
            return {"op": op, "control": control}

        elif op in ["add", "sub"]:
            # add、sub 不需訪存，原值直接帶到 WB
            print(f"[MEM] {op.upper()} -> No memory access needed, Control Signals: {control}")
            return {
                "op": op,
                "result": executed_result["result"],
                "rd": executed_result["rd"],
                "control": control
            }

    ## --------------------- WB 階段 --------------------- ##
    def write_back(self, mem_result):
        """模擬 WB 階段 (寫回)"""
        if not mem_result:
            return

        op = mem_result["op"]
        control = mem_result["control"]
        # 只有 lw、add、sub 需要寫回暫存器
        if op in ["lw", "add", "sub"]:
            result = mem_result.get("data", mem_result.get("result"))
            rd_index = mem_result.get("rd")
            if rd_index is not None:
                self.registers[rd_index] = result
                print(f"[WB] Writing Back -> Register[{rd_index}] = {result}, Control Signals: {control}")
        else:
            print(f"[WB] No Register Write needed, Control Signals: {control}")

    ## --------------------- Data Hazard (Forwarding) --------------------- ##
    def get_forwarded_value(self, path, reg_index):
        """根據 Forward 信號決定要讀哪個來源的值"""
        if path == "A":
            if self.ForwardA == "10" and self.EX_MEM and "result" in self.EX_MEM:
                return self.EX_MEM["result"]
            elif self.ForwardA == "01" and self.MEM_WB and "result" in self.MEM_WB:
                return self.MEM_WB["result"]
        elif path == "B":
            if self.ForwardB == "10" and self.EX_MEM and "result" in self.EX_MEM:
                return self.EX_MEM["result"]
            elif self.ForwardB == "01" and self.MEM_WB and "result" in self.MEM_WB:
                return self.MEM_WB["result"]
        # 若無 forward，就直接從暫存器取值
        return self.registers[reg_index]

    def detect_forwarding_signals(self, decoded_instruction):
        """檢測要不要 Forward 到 EX 階段 (EX Hazard / MEM Hazard)"""
        self.ForwardA = "00"
        self.ForwardB = "00"
        op = decoded_instruction["op"]

        # EX/MEM Hazard
        if self.EX_MEM and self.EX_MEM.get("rd") is not None:
            ex_rd = self.EX_MEM["rd"]
            # 如果上一階段 (EX/MEM) 的目標暫存器 == 目前 instruction 的 rs/rt
            if ex_rd == decoded_instruction.get("rs"):
                self.ForwardA = "10"
            if ex_rd == decoded_instruction.get("rt"):
                self.ForwardB = "10"

        # MEM/WB Hazard
        if self.MEM_WB and self.MEM_WB.get("rd") is not None:
            mem_rd = self.MEM_WB["rd"]
            if mem_rd == decoded_instruction.get("rs") and self.ForwardA != "10":
                self.ForwardA = "01"
            if mem_rd == decoded_instruction.get("rt") and self.ForwardB != "10":
                self.ForwardB = "01"

        # 如果是 sw，需要判斷是否要 forward 給 sw 要寫到記憶體的 register
        if op == "sw":
            reg = decoded_instruction["reg"]  # sw $reg, offset($base)
            # EX/MEM Hazard
            if self.EX_MEM and self.EX_MEM.get("rd") == reg:
                self.ForwardB = "10"
            # MEM/WB Hazard
            if self.MEM_WB and self.MEM_WB.get("rd") == reg and self.ForwardB != "10":
                self.ForwardB = "01"

    ## --------------------- Data Hazard (Stall) --------------------- ##
    def detect_hazard_lw_stall(self):
        """
        檢測是否需要對 lw 進行 stall：
        若前一指令是 lw，而下一指令馬上使用了 lw 的目標暫存器，則需要 stall。
        """
        if self.ID_EX and self.ID_EX["op"] == "lw":
            rd = self.ID_EX["reg"]
            if self.IF_ID:  # 目前正在 IF -> ID 的指令
                instr = self.IF_ID.split()
                if instr[0] in ["add", "sub"]:
                    rs = int(instr[2].replace(",", "").replace("$", ""))
                    rt = int(instr[3].replace(",", "").replace("$", ""))
                    if rd in [rs, rt]:
                        print(f"[Stall] Data Hazard detected: lw ${rd} -> stalling pipeline")
                        return True
                elif instr[0] == "beq":
                    rs = int(instr[1].replace(",", "").replace("$", ""))
                    rt = int(instr[2].replace(",", "").replace("$", ""))
                    if rd in [rs, rt]:
                        print(f"[Stall] Data Hazard detected: lw ${rd} -> stalling pipeline")
                        return True
        
        return False

    ## --------------------- Pipeline Step --------------------- ##
    def step(self, instruction):
        """
        一個 Cycle 的處理：
        1. 先看是否需要 lw stall。若需要，整條 pipeline 退一拍（插入 NOP）。
        2. 順序執行 WB、MEM、EX、ID、IF。
        """
        # 如果 pipeline 已空且沒有新指令，則不繼續前進
        if not (self.IF_ID or self.ID_EX or self.EX_MEM or self.MEM_WB or instruction):
            return False

        # 先判斷 lw hazard，需要 stall 就不更新 IF/ID
        need_stall = self.detect_hazard_lw_stall()

        # ---------- 寫回 (WB) ----------
        if self.MEM_WB:
            self.write_back(self.MEM_WB)
            self.MEM_WB = None

        # ---------- 訪存 (MEM) ----------
        if self.EX_MEM:
            self.MEM_WB = self.memory_access(self.EX_MEM)
            self.EX_MEM = None

        # ---------- 執行 (EX) ----------
        if self.ID_EX:
            self.EX_MEM = self.execute(self.ID_EX)
            self.ID_EX = None

        # ---------- 譯碼 (ID) ----------
        if not need_stall and self.IF_ID:
            self.ID_EX = self.decode(self.IF_ID)
            self.IF_ID = None
        else:
            # 如果需要 stall，則不 decode，新一級的 IF/ID 依然保持不動
            pass

        # ---------- 取指 (IF) ----------
        if not need_stall and instruction:
            self.IF_ID = self.fetch(instruction)

        # Cycle 結束：+1 並列印管線狀態 (只印一次)
        self.cycle += 1
        self.print_pipeline_state()
        return True

    ## --------------------- 輔助列印函式 --------------------- ##
    def print_pipeline_state(self):
        """列印本 Cycle 中，各級暫存器對應的指令/控制訊號狀態。"""
        print(f"Cycle {self.cycle} Pipeline State:")
        
        # IF/ID
        if self.IF_ID:
            print(f"  IF/ID: {self.IF_ID}")
        else:
            print("  IF/ID: None")
        
        # ID/EX
        if self.ID_EX:
            c = self.ID_EX["control"]
            print(f"  ID/EX: (op={self.ID_EX['op']}) | "
                  f"Signals: RegDst={c['RegDst']}, ALUSrc={c['ALUSrc']}, "
                  f"MemRead={c['MemRead']}, MemWrite={c['MemWrite']}, "
                  f"MemtoReg={c['MemtoReg']}, RegWrite={c['RegWrite']}, "
                  f"Branch={c['Branch']}, ALUOp={c['ALUOp']}")
        else:
            print("  ID/EX: None | Signals: RegDst=X, ALUSrc=X, MemRead=X, "
                  "MemWrite=X, MemtoReg=X, RegWrite=X, Branch=X, ALUOp=X")
        
        # EX/MEM
        if self.EX_MEM:
            c = self.EX_MEM["control"]
            print(f"  EX/MEM: (op={self.EX_MEM['op']}) | "
                  f"Signals: Branch={c['Branch']}, MemRead={c['MemRead']}, "
                  f"MemWrite={c['MemWrite']}, RegWrite={c['RegWrite']}, "
                  f"MemtoReg={c['MemtoReg']}")
        else:
            print("  EX/MEM: None | Signals: Branch=X, MemRead=X, MemWrite=X, RegWrite=X, MemtoReg=X")
        
        # MEM/WB
        if self.MEM_WB:
            c = self.MEM_WB["control"]
            print(f"  MEM/WB: (op={self.MEM_WB['op']}) | "
                  f"Signals: RegWrite={c['RegWrite']}, MemtoReg={c['MemtoReg']}")
        else:
            print("  MEM/WB: None | Signals: RegWrite=X, MemtoReg=X")
        
        print()

    def print_final_state(self):
        """列印最終暫存器、記憶體及 Cycle 計數。"""
        print("\nFinal Register Values:")
        for i in range(32):
            print(f"${i}={self.registers[i]}", end=" ")
        print("\n\nFinal Memory Values:")
        for i in range(32):
            print(f"M[{i}]={self.memory[i]}", end=" ")
        print(f"\n\nTotal Cycles: {self.cycle}\n")
