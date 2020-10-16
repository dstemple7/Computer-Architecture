"""CPU functionality."""

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.flg = [0] * 8
        self.pc = 0
        self.halted = False
        self.branch_table = {}
        self.branch_table[HLT] = self.HLT
        self.branch_table[LDI] = self.LDI
        self.branch_table[PRN] = self.PRN
        self.branch_table[MUL] = self.MUL
        self.branch_table[POP] = self.POP
        self.branch_table[PUSH] = self.PUSH
        self.branch_table[CALL] = self.CALL
        self.branch_table[RET] = self.RET
        self.branch_table[ADD] = self.ADD
        self.branch_table[CMP] = self.CMP
        self.branch_table[JEQ] = self.JEQ
        self.branch_table[JMP] = self.JMP
        self.branch_table[JNE] = self.JNE
        self.sp = 7
    
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
            self.reg[self.ram[reg_a]] += self.reg[self.ram[reg_b]]
            self.pc += 3
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[self.ram[reg_a]] *= self.reg[self.ram[reg_b]]
            self.pc += 3
        elif op == "CMP":
            if self.reg[self.ram[reg_a]] == self.reg[self.ram[reg_b]]:
                self.flg[7] = 1
            elif self.reg[self.ram[reg_a]] > self.reg[self.ram[reg_b]]:
                self.flg[6] = 1
            elif self.reg[self.ram[reg_a]] < self.reg[self.ram[reg_b]]:
                self.flg[5] = 1
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

    def ADD(self):
        self.alu("ADD", self.pc+1, self.pc+2)

    def CMP(self):
        # *This is an instruction handled by the ALU.*
        # `CMP registerA registerB`
        # Compare the values in two registers.
        # * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
        # * If registerA is less than registerB, set the Less-than `L` flag to 1,  otherwise set it to 0.
        # * If registerA is greater than registerB, set the Greater-than `G` flag to 1, otherwise set it to 0.
        self.alu("CMP", self.pc+1, self.pc+2)

    def JEQ(self):
        # If `greater-than` flag flg[6] or `equal` flag flg[7] is set (true), jump to the address stored in the given register.
        if self.flg[7] == 1:
            self.pc = self.reg[self.ram[self.pc+1]]
        else:
            self.pc += 2

    def JMP(self):
        # Jump to the address stored in the given register
        # Set the `PC` to the address stored in the given register
        given_register = self.reg[self.ram[self.pc+1]]
        self.pc = given_register

    def JNE(self):
        # If `E` flag flg[7] is clear (false, 0), jump to the address stored in the given register.
        if self.flg[7] == 0:
            self.pc = self.reg[self.ram[self.pc+1]]
        else:
            self.pc += 2

    def PUSH(self):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]
        self.ram[self.reg[self.sp]] = val
        self.pc += 2

    def POP(self):
        addr = self.reg[self.sp]
        val = self.ram[addr]
        self.reg[self.ram[self.pc + 1]] = val
        self.reg[self.sp] += 1
        self.pc += 2

    def CALL(self):
        # addr = self.pc + 2
        # self.reg[6] -= 1
        # self.ram[self.reg[6]] = addr
        # self.pc = self.reg[self.ram_read(self.pc + 1)]
        given_register = self.ram[self.pc + 1]
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc = self.reg[given_register]

    def RET(self):
        # SP = self.ram[self.reg[6]]
        # self.pc = SP
        # self.reg[6] += 1
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def run(self):
        """Run the CPU."""
        while not self.halted:
            # internal_registers = self.ram_read(self.pc)
            # if internal_registers in self.branch_table:
            #     self.branch_table[internal_registers]()
            IR = self.pc
            instance = self.ram[IR]

            try:
                self.branch_table[instance]()
            
            except KeyError:
                print(f"{self.reg[self.ram[instance]]}")
                sys.exit(1)