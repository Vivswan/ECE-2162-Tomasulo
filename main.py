import pathlib

from src.instruction.instruction import print_str_instructions
from src.tomasulo import Tomasulo
from unit_tests import test_codes

if __name__ == '__main__':
    for test_case in [0]:
        print(f"Running Test Case {test_case}...")
        str_result = ""
        code = test_codes[test_case]
        tomasulo = Tomasulo(code).run()

        print("\n".join([str(i) for i in tomasulo.instruction_buffer.history]) + "\n")
        str_result += print_str_instructions(tomasulo.instruction_buffer.history)
        str_result += "\n"

        str_result += tomasulo.rat.print_str_tables()
        str_result += tomasulo.memory_unit.print_str_tables()
        str_result += "\n"

        assert_result, asserts = tomasulo.check_asserts()
        str_result += "\n".join([str(i) for i in asserts]) + "\n"
        str_result += f"asserts: {assert_result}"

        print(str_result)
        print()
        print()

        path = pathlib.Path(__file__).parent.resolve().joinpath(f"result/result_{test_case}.txt")
        with open(path, "w") as file:
            file.write(str_result.replace("\u0336", ""))
