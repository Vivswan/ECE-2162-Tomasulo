from src.component.computation_units.base_class import ComputationUnit
from src.component.intruction import Instruction, InstructionType
from src.component.registers.rat import RAT


class Memory(ComputationUnit):
    instruction_type = [InstructionType.LD, InstructionType.SD]

    # TODO: implement Queue
    def __init__(self, rat: RAT, latency: int, latency_mem: int, num_rs: int):
        super().__init__(rat, latency, num_rs)
        self.latency_mem = latency_mem
        self.data = {}

    def decode_instruction(self, instruction: Instruction):
        instruction.operands[1] = int(instruction.operands[1])
        instruction.operands[2] = self.rat.get(instruction.operands[2])

        if instruction.type == InstructionType.LD:
            instruction.operands[0] = self.rat.reserve_rob(instruction.operands[0])
            instruction.destination = instruction.operands[0]
        if instruction.type == InstructionType.SD:
            instruction.operands[0] = self.rat.get(instruction.operands[0])
            instruction.destination = "NOP"

    def step_execute(self, cycle, instruction: Instruction):
        if self.resolve_operand(instruction, 2):
            memory_address = instruction.operands[1] + instruction.operands[2]
            if memory_address % 4 != 0:
                raise Exception(f"Invalid memory address: {memory_address} % 4 != 0")

            if "memory_address" not in instruction.related_data:
                instruction.related_data["memory_address"] = memory_address
                instruction.stage_event.execute = (cycle, cycle + self.latency - 1)

            for instr in self.buffer_list:
                if instruction.type == InstructionType.LD and instr.type == InstructionType.SD:
                    if instr.counter_index < instruction.counter_index and instr.related_data[
                        "memory_address"] == memory_address:
                        return False

            if instruction.type == InstructionType.LD:
                instruction.result = self.data[memory_address] if memory_address in self.data else 0
            elif instruction.type == InstructionType.SD and self.resolve_operand(instruction, 0):
                self.data[memory_address] = instruction.operands[0]
                instruction.result = True
            else:
                return False

            exe = instruction.stage_event.execute[1]
            if instruction.type == InstructionType.LD:
                instruction.stage_event.memory = (exe + 1, exe + self.latency_mem)
            if instruction.type == InstructionType.SD:
                instruction.stage_event.commit = (exe + 1, exe + self.latency_mem)
            return True

        return False

    def has_result(self, cycle: int) -> bool:
        for instr in self.buffer_list:
            if instr.type != InstructionType.SD:
                continue
            if instr.stage_event.commit is not None and instr.stage_event.commit[1] <= cycle:
                self.remove_instruction(instr)
        return super().has_result(cycle)

    def peak_result(self, cycle: int):
        self.has_result(cycle)
        return super().peak_result(cycle)
