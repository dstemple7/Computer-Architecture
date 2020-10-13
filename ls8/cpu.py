"""CPU functionality."""

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.halted = False
        self.branch_table = {}
        self.branch_table[HLT] = self.HLT
        self.branch_table[LDI] = self.LDI
        self.branch_table[PRN] = self.PRN
        self.branch_table[MUL] = self.MUL
    
    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print('need 2nd arg')
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()

                    if line == '' or line[0] == '#':
                        continue
                    else:
                        self.ram[address] = int(line.split()[0], 2)

                    address += 1                    
        except FileNotFoundError:
            print(f'{sys.argv[0]} {sys.argv[1]} not found')
            sys.exit(2)

    # should accept the address to read and return the value stored there.
    # Memory Address Register (MAR) contains the address that is being read or written to
    def ram_read(self, MAR):
        return self.ram[MAR]

    # should accept a value to write, and the address to write it to.
    # Memory Data Register (MDR) contains the data that was read or the data to write
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[self.ram[reg_a]] *= self.reg[self.ram[reg_b]]
            self.pc += 3
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
        self.halted = True

    # LDI Register Immediate
    # sets a specified register to a specified value.
    def LDI(self):
        register = self.ram_read(self.pc+1)
        val = self.ram_read(self.pc+2)
        self.reg[register] = val
        self.pc += 3

    # `PRN register` pseudo-instruction
    # Print numeric value stored in the given register.
    def PRN(self):
        register = self.ram_read(self.pc+1)
        print(self.reg[register])
        self.pc +=2

    def MUL(self):
        self.alu("MUL", self.pc+1, self.pc+2)

    def run(self):
        """Run the CPU."""

        while not self.halted:
            internal_registers = self.ram_read(self.pc)
            if internal_registers in self.branch_table:
                self.branch_table[internal_registers]()