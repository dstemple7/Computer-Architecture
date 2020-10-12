"""CPU functionality."""

import sys

# pulled from printl8.ls8 example file
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.halted = False

    # should accept the address to read and return the value stored there.
    # Memory Address Register (MAR) contains the address that is being read or written to
    def ram_read(self, MAR):
        return self.ram[MAR]

    # should accept a value to write, and the address to write it to.
    # Memory Data Register (MDR) contains the data that was read or the data to write
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR
    
    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # HALT
    # like exit() in python
    def HLT(self):
        self.halted = False

    # LDI Register Immediate
    # sets a specified register to a specified value.
    def LDI(self, register, MDR):
        self.reg[register] = MDR

    # `PRN register` pseudo-instruction
    # Print numeric value stored in the given register.
    def PRN(self, register):
        print(self.reg[register])

    def run(self):
        """Run the CPU."""

        while not self.halted:
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            instruction_register = self.pc
            instruction = self.ram[instruction_register]

            # # Set the value of a register to an integer.
            if instruction == LDI:
                self.LDI(operand_a, operand_b)
                self.pc += 2

            # Print to the console the decimal integer value that is stored in the given register.
            elif instruction == PRN:
                self.PRN(operand_a)
                self.pc += 1

            # exit the loop if a HLT instruction is encountered, regardless of whether or not there are more lines of code in the LS-8 program you loaded.We can consider HLT to be similar to Python's exit() in that we stop whatever we are doing, wherever we are.
            elif instruction == HLT:
                self.halted = True
            self.pc += 1
