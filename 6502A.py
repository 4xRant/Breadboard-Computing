#  http://www.6502asm.com/beta/index.html

# 54

import curses
from curses import wrapper
import RPi.GPIO as GPIO
from time import sleep
import fileinput
#   LDY # = immediate mode 
#   x02 the x prefix indicates no instruction, acts as NOP
#   * = new
instr=[
"brk","ora (zp+x)","x02",        "x03","TSP zp*","ora","ASL zp",  "RMB0*","PHP","ora","asl","x0b","0c","ora","ASL a16","BBR0*",
"bpl","ora (zp),y","ORA (zp)*",  "x13","TRB zp*","ora","ASL zp,x","RMB1*","CLC","ora","1a","x1b","1c","ora","ASL a16,x","BBR1*",
"JSR","AND (zp+x)","x22",        "x23","BIT zp","AND zp","rol",   "RMB2*","plp","AND #","ROL A","x2b","BIT a16","AND a16","ROL a16","BBR2*",
"BMI r","AND (zp),y","AND (zp)*","x33","BIT zp,x*","and","rol",   "RMB3*","SEC","and","3a","x3b","3c","and","ROL a16,x","BBR3*",
"rti","eor (zp+x)","x42",        "x43","44","eor","lsr",      "RMB4*","pha","eor","LSR","x4b","JMP a16","EOR a16","LSR a16","BBR4*",
"BVC r","eor (zp),y","EOR (zp)*","x53","54","eor","lsr",      "RMB5*","CLI","EOR a16,y","5a","x5b","5c","eor","lsr","BBR5*",
"RTS","adc (zp+X)","x62",        "x63","64","adc","ROR zp",   "RMB6*","PLA","ADC #","ROR A","x6b","JMP a16","ADC a16","ROR a16","BBR6*",
"BVS r","adc (zp),y","ADC (zp)*","x73","74","adc","ROR zp,x", "RMB7*","sei","adc","7a","x7b","JMP*(a16,x)",  "adc","ROR a16,x","BBR7*",
"BRA r*", "STA (zp+X)","x82",    "x83","STY zp","STA zp","STX zp", "SMB0*","dey","89","txa","x8b","STY a16","STA a16","STX a16","BBS0*",
"BCC r","STA (zp),y","STA (zp)*","x93","94", "STA zp,x","STX zp,y","SMB1*","tya","STA a16,y","txs","x9b","9c","STA a16,x","9e","BBS1*",
"LDY #","LDA (zp+X)","LDX #",    "xa3","ldy","LDA zp","LDX",   "SMB2*","TAY","LDA #","TAX","xab","ldy","LDA a16","LDX","BBS2*",
"BCS r","LDA (zp),y","LDA (zp)*","xb3","ldy","LDA zp,x","LDX", "SMB3*","CLV","LDA a16,y","TSX","xbb","ldy","LDA a16,x","LDX a16,y","BBS3*",
"CPY #","cmp (zp+X)","c2",       "xc3","cpy","cmp","dec",    	 "SMB4*","INY","cmp","DEX","WAI*","cpy","cmp","dec","BBS4*",
"BNE r","cmp (zp),y","CMP (zp)*","xd3","d4","cmp","dec",       "SMB5*","CLD","cmp","da","STP*","dc","cmp","dec","BBS5*",
"CPX #","sbc (zp+X)","e2",       "xe3","cpx","sbc","inc",      "SMB6*","INX","SBC #","NOP","eb","cpx","sbc","inc","BBS6*",
"BEQ r","sbc (zp),y","SBC (zp)*","xf3","f4","sbc","inc",       "SMB7*","SED","sbc","fa","fb","fc","sbc","fd","BBS7*"]
hexdump = "xx"
lastaddress = 0
newaddress = 0
clkpulses = 0
nInstructionTicks = 1
PIN_RESET = 8
PIN_6502CLK_PULSE = 17
PIN_MONITOR25_IN = 25 # A0-A7
PIN_MONITOR18_IN = 18 # d0 - d7
PIN_MONITOR23_IN = 23 # flags
PIN_MONITOR24_IN = 24 # A8-A15
PIN_MONITOR_CLK = 16
PIN_MONITOR_LATCH = 26
PIN_D1 = 19
PIN_D2 = 13
PIN_D3 = 6
PIN_D4 = 5
PIN_D5 = 11
PIN_D6 = 9
PIN_D7 = 10
PIN_D8 = 22
PIN_D245_OE = 2
PIN_LED = 15
PIN_RUN_PROGRAM = 3  # LOW = RUN (A)  HIGH = PROGRAM (B) 157 control
PIN_ROM_WE = 4
flagPINLED = GPIO.LOW
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RESET, GPIO.OUT)
GPIO.output(PIN_RESET, GPIO.HIGH)
GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.output(PIN_LED, flagPINLED)
GPIO.setup(PIN_6502CLK_PULSE, GPIO.OUT)
GPIO.setup(PIN_MONITOR25_IN, GPIO.IN)
GPIO.setup(PIN_MONITOR18_IN, GPIO.IN)
GPIO.setup(PIN_MONITOR23_IN, GPIO.IN)
GPIO.setup(PIN_MONITOR24_IN, GPIO.IN)
GPIO.setup(PIN_MONITOR_CLK, GPIO.OUT)
GPIO.setup(PIN_MONITOR_LATCH, GPIO.OUT)
GPIO.output(PIN_MONITOR_CLK, GPIO.LOW)
GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
GPIO.setup(PIN_RUN_PROGRAM, GPIO.OUT)
GPIO.setup(PIN_ROM_WE, GPIO.OUT)
GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) # LOW = run mode
GPIO.output(PIN_ROM_WE, GPIO.HIGH)
GPIO.setup(PIN_D1, GPIO.OUT)
GPIO.setup(PIN_D2, GPIO.OUT)
GPIO.setup(PIN_D3, GPIO.OUT)
GPIO.setup(PIN_D4, GPIO.OUT)
GPIO.setup(PIN_D5, GPIO.OUT)
GPIO.setup(PIN_D6, GPIO.OUT)
GPIO.setup(PIN_D7, GPIO.OUT)
GPIO.setup(PIN_D8, GPIO.OUT)
GPIO.setup(PIN_D245_OE, GPIO.OUT)
GPIO.output(PIN_D245_OE, GPIO.HIGH) # turn data 245 OE high, so that it is off.

def main(stdscr):
	global lastaddress
	global newaddress
	global clkpulses
	global nInstructionTicks
	sStartAddress = "8400"
	sLastFileName = "6502prg2"
	
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.cbreak()
	curses.flash()
	curses.noecho()
	stdscr.addstr(1, 1, "r/R-Reset:8400 ")
	#stdscr.addstr(2, 1, "p-Pulse CPU clock")
	stdscr.addstr(3, 1, "l-Pulse LED")
	#stdscr.addstr(4, 1, "y-Latch on")
	#stdscr.addstr(5, 1, "u-Latch off")
	#stdscr.addstr(6, 1, "i-Serial Input")
	#stdscr.addstr(7, 1, "d-Set Data Byte:")
	#stdscr.addstr(8, 1, "h-Toggle Data 245 OE")
	#stdscr.addstr(9, 1, "f-File input")
	stdscr.addstr(10, 1, "w-Write 6502hexdump")
	stdscr.addstr(11, 1, "q/Q-Write file:6502prg2")
	stdscr.addstr(12, 1, "s/S-Step one tick")
	stdscr.addstr(13, 1, "1-Step  10 CPU ticks")
	stdscr.addstr(14, 1, "2-Step  50 CPU ticks")
	stdscr.addstr(15, 1, "3-Step 100 CPU ticks")
	stdscr.addstr(16, 1, "4-Step 500 CPU ticks")
	stdscr.addstr(17, 1, "5-Step until NOP")
	stdscr.addstr(18, 1, "t-Test/Read block")
	stdscr.addstr(21, 1, "X-Exit------------------------------------------------------------------------")
	stdscr.addstr(22, 1, "FF8A:")
	stdscr.addstr(23, 1, "     BCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF")
	stdscr.addstr(24, 1, "          9               A               B               C")
	logscr = curses.newwin(20, 50, 1, 30)
	clkpulses = 0
	flagPINLED = GPIO.LOW
	GPIO.output(PIN_LED, flagPINLED)
	while 1 == 1:
		stdscr.addstr(20, 0,"?             ")
		curses.echo()
		stdscr.refresh()
		k = stdscr.getch(20, 1)
		stdscr.addstr(20, 5, "[" + str(k) + "]")
		if (k == 114 or k == 82): # reset
			setDataByte(0)
			GPIO.output(PIN_D245_OE, GPIO.HIGH) # go into program mode
			GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH)
			if k == 114: #r ask for new address
				stdscr.addstr(1, 1, "r---Reset?              ")
				sStartAddress = stdscr.getstr(1, 11, 4).decode(encoding="utf-8")
			stdscr.addstr(1, 1, "r/R-Resetting->   ")
			stdscr.refresh()
			logscr.scrollok(True)
			logscr.scroll(1)
			logscr.refresh()
			stdscr.refresh()
			sleep(0.2) 
			clkpulses = 0
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)  # should be low already, but just in case.
			#stdscr.addstr(2, 1, "p-Pulse CPU clock:" + str(clkpulses))
			GPIO.output(PIN_RESET, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW")
			logscr.refresh()
			sleep(0.2)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1")
			logscr.refresh()
			sleep(0.2)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1..2")
			logscr.refresh()
			sleep(0.2)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1..2..3")
			logscr.refresh()
			sleep(0.1)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1..2..3..4")
			logscr.refresh()
			sleep(0.1)
			GPIO.output(PIN_RESET, GPIO.HIGH)
			logscr.addstr(19, 1, "RESET LOW PULSE 1..2..3..4, RESET HIGH")
			sleep(1)
			logscr.scroll(1)
			logscr.refresh()

			intDataHEX = int(sStartAddress[2:4],16)
			setDataByte(intDataHEX)
			GPIO.output(PIN_D245_OE, GPIO.HIGH)  # output enable
			
			x = 1
			while newaddress != 65532 and x < 15:  # fffc
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				sleep(0.01)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				readMonitor(logscr, stdscr)
				sleep(0.1)
				x = x + 1

			clkpulses = clkpulses + 1
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			readMonitor(logscr, stdscr)
			sleep(0.1)
			
			intDataHEX = int(sStartAddress[0:2],16)
			setDataByte(intDataHEX)
			GPIO.output(PIN_D245_OE, GPIO.HIGH)
			readMonitor(logscr, stdscr)
			clkpulses = clkpulses + 1
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			readMonitor(logscr, stdscr)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			GPIO.output(PIN_D245_OE, GPIO.LOW)
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)
			readMonitor(logscr, stdscr)
			stdscr.addstr(1, 1, "r/R-Reset:" + sStartAddress + "  ")
			#stdscr.addstr(2, 1, "p-Pulse CPU clock:         ")
			stdscr.refresh()
			logscr.refresh()
			clkpulses = 0
			
		elif k == 88: # X-Exit
				break
		elif k == 112:
				clkpulses = clkpulses + 1
				stdscr.addstr(2,1,"p-Pulse CPU clock:" + str(clkpulses))
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH) #program mode disables RAM OE
				GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
				readMonitor(logscr, stdscr)
				lastaddress = newaddress
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 Disable
				GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) # 'A' = run mode, enables RAM OE
				readMonitor(logscr, stdscr)
				#GPIO.output(PIN_ROM_OE, GPIO.HIGH) #output rom disable
				lastaddress = newaddress

		elif k == 115: # s-Step
				GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
				GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				readMonitor(logscr, stdscr)
				lastaddress = newaddress

		elif k == 83: # S-Step, do not monitor low clock
				GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
				GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				#readMonitor(logscr)
				lastaddress = newaddress

		elif k == 49: # 1 10 steps
			x = 0
			GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
			while x < 10:
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				#readMonitor(logscr)
				lastaddress = newaddress
				x = x + 1

		elif k == 50: # 2 50 steps
			x = 0
			GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
			while x < 50:
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				#readMonitor(logscr)
				lastaddress = newaddress
				x = x + 1

		elif k == 51: # 3 100 steps
			x = 0
			GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
			while x < 100:
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				#readMonitor(logscr)
				lastaddress = newaddress
				x = x + 1

		elif k == 52: # 4 500 steps
			x = 0
			GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
			while x < 500:
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				#readMonitor(logscr)
				lastaddress = newaddress
				x = x + 1

		elif k == 53: # 5 run until NOP
			x = 0
			GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
			instruction = '';
			while x < 5000 and instruction != "NOP":
				clkpulses = clkpulses + 1
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				instruction = readMonitor(logscr, stdscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				lastaddress = newaddress
				x = x + 1

		elif k == 108: # l-Pulse
				flagPINLED = GPIO.LOW if flagPINLED == GPIO.HIGH else GPIO.HIGH
				GPIO.output(PIN_LED, flagPINLED)
		elif k == 105:
				readMonitor(logscr, stdscr)
		elif k == 117:
				stdscr.addstr(4, 1, "y-Latch on")
				stdscr.addstr(5, 1, "u-Latch OFF")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
		elif k == 121:
				stdscr.addstr(4, 1, "y-Latch ON")
				stdscr.addstr(5, 1, "u-Latch off")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
		elif k == 68 or k == 100: # D
				GPIO.output(PIN_D245_OE, GPIO.LOW)
				stdscr.addstr(7, 1, "D-Set Data Byte?     ")
				sDataHEX = stdscr.getstr(7,18, 2).decode(encoding="utf-8")
				intDataHEX = int(sDataHEX, 16)
				stdscr.addstr(7, 1, "D-Set Data Byte:")
				setDataByte(intDataHEX)
				stdscr.refresh()
		elif k == 104:  # h
			GPIO.output(PIN_D245_OE, GPIO.LOW if GPIO.input(PIN_D245_OE) else GPIO.HIGH)
			
		elif k == 102: # f read file
			readFile("6502hexdump.txt")
			stdscr.addstr(10, 1, hexdump)
			stdscr.refresh()
			
		elif k == 119: #w - write data to memory
			readFile("6502hexdump.txt")
			writeToMemory(logscr, stdscr)
			
		elif k == 113: #q- ask for ML file then write
			stdscr.addstr(11, 1, "q/Q-Write file?              ")
			stdscr.refresh()
			sFileName = stdscr.getstr(11, 16, 20).decode(encoding="utf-8")
			sLastFileName = sFileName
			readFile(sFileName)
			writeToMemory(logscr, stdscr)
			stdscr.addstr(11, 1, "q/Q-Write file:")
			stdscr.refresh()
		
		elif k == 81: #Q reload last file
			stdscr.addstr(11, 1, "q/Q-Write file>")
			stdscr.refresh()
			readFile(sLastFileName)
			writeToMemory(logscr, stdscr)
			stdscr.addstr(11, 1, "q/Q-Write file:")
			stdscr.refresh()
			
		elif k == 116: # t-Test/Read
			testMemoryBlock(10, logscr, stdscr)
			
	print("exiting...")
	curses.flash()

def readMonitor(logscr, stdscr):
	global lastaddress
	global newaddress
	global clkpulses
	global instr
	global nInstructionTicks
	addrbyte1 = 0
	addrbyte2 = 0
	returnvalue = ""
	logscr.scrollok(True)
	logscr.scroll(1)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
	
	pinnumber = 0
	flagsbyte = 0
	databyte = 0
	addrbyte1 = 0
	addrbyte2 = 0
	while pinnumber < 8:
		databit = GPIO.input(PIN_MONITOR18_IN)
		flagsbyte = flagsbyte + databit * pow(2, pinnumber)
		databit = GPIO.input(PIN_MONITOR23_IN)
		databyte = databyte + databit * pow(2, pinnumber)
		databit = GPIO.input(PIN_MONITOR24_IN)
		addrbyte1 = addrbyte1 + databit * pow(2, pinnumber)
		databit = GPIO.input(PIN_MONITOR25_IN)
		addrbyte2 = addrbyte2 + databit * pow(2, pinnumber)
		GPIO.output(PIN_MONITOR_CLK, GPIO.HIGH)
		pinnumber = pinnumber + 1
		GPIO.output(PIN_MONITOR_CLK, GPIO.LOW)		
		
	#flagsbyte = readMonitor8bits()


	if flagsbyte & 1:
		logscr.addstr(19, 27, "r")
	else:
		logscr.addstr(19, 27, "W", curses.color_pair(1))

	if flagsbyte & 16: # High clock
		logscr.addstr(19, 11, "H")
		nInstructionTicks = nInstructionTicks + 1
	else:
		logscr.addstr(19, 11, "l")
		
	logscr.addstr(19, 12, "P" if flagsbyte & 128 else "r")  #program  / run
	
	if flagsbyte & 64: # Sync high
		logscr.addstr(19, 13, "S", curses.color_pair(3))
	else:
		logscr.addstr(19, 13, " ")
		
	#databyte = readMonitor8bits()
	logscr.addstr(19, 28, ':' + (hex(databyte)[2:4] if databyte > 15 else "0" + hex(databyte)[2:4]))

	if flagsbyte & 64 and flagsbyte & 16: # Sync and High clock
		logscr.addstr(19, 15, instr[databyte])
		nInstructionTicks = 1
		returnvalue = instr[databyte]

	logscr.addstr(19, 1, "[#" + str(clkpulses) + "." + str(nInstructionTicks) + " ]" )
	
	#addrbyte1 = readMonitor8bits()
	logscr.addstr(19, 32, 'addr:' + (hex(addrbyte1)[2:4] if addrbyte1 > 15 else "0" + hex(addrbyte1)[2:4]))

	#l = readMonitor8bits()
	logscr.addstr(19, 39, hex(addrbyte2)[2:4] if addrbyte2 > 15 else "0" + hex(addrbyte2)[2:4])
	
	newaddress = addrbyte1 * 256 + addrbyte2
	if newaddress != lastaddress:
		logscr.addstr(19, 41, " *")
		
	if newaddress > 65418 and newaddress < 65488:  # ff8b -> ffcf
		if databyte > 31 and databyte < 127:
			stdscr.addstr(22, newaddress - 65413, chr(databyte))
		else:
			stdscr.addstr(22, newaddress - 65413, ' ')
		stdscr.refresh()
	
	logscr.refresh()
	return returnvalue
	
def readMonitor8bits():
	pinnumber = 0
	databyte = 0
	while pinnumber < 8:
		databit = GPIO.input(PIN_MONITOR_IN)
		databyte = databyte + databit * pow(2, pinnumber)
		GPIO.output(PIN_MONITOR_CLK, GPIO.HIGH)
		pinnumber = pinnumber + 1
		GPIO.output(PIN_MONITOR_CLK, GPIO.LOW)				
	return databyte

def setDataByte(intDataHEX):
	GPIO.output(PIN_D245_OE, GPIO.LOW) # goes through a NAND gate to set OE HIGH (245 no output)
	GPIO.output(PIN_D1, GPIO.HIGH if intDataHEX & 1 else GPIO.LOW)
	GPIO.output(PIN_D2, GPIO.HIGH if intDataHEX & 2 else GPIO.LOW)
	GPIO.output(PIN_D3, GPIO.HIGH if intDataHEX & 4 else GPIO.LOW)
	GPIO.output(PIN_D4, GPIO.HIGH if intDataHEX & 8 else GPIO.LOW)
	GPIO.output(PIN_D5, GPIO.HIGH if intDataHEX & 16 else GPIO.LOW)
	GPIO.output(PIN_D6, GPIO.HIGH if intDataHEX & 32 else GPIO.LOW)
	GPIO.output(PIN_D7, GPIO.HIGH if intDataHEX & 64 else GPIO.LOW)
	GPIO.output(PIN_D8, GPIO.HIGH if intDataHEX & 128 else GPIO.LOW)

def readFile(sFileName):
	global hexdump
	hexdump = ""
	sFileName = sFileName + ".txt"
	with fileinput.input(files=(sFileName)) as f:
		for line in f:
			processLine(line.replace(" ", ""))

def processLine(line):
	global hexdump
	line = (line + ";").split(';')[0]
	hexdump = hexdump + line.strip()

def writeToMemory(logscr, stdscr):
	global hexdump
	global clkpulses
	logscr.scrollok(True)
	logscr.scroll(1)
	GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH) #B = program mode
	readMonitor(logscr, stdscr)
	pos = 0
	while hexdump[pos:pos+2] != "xx":
		bb = int(hexdump[pos:pos+2], 16)
		setDataByte(bb)
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		pulseROMWE(logscr, stdscr)
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		setDataByte(234) #ea / nop
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		#sleep(0.01)
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		#sleep(0.01)
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		#sleep(0.01)
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		
		logscr.refresh()
		#sleep(0.01)
		pos = pos + 2
		
	GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)  # A-run mode
	logscr.scroll(1)
	logscr.addstr(19, 1, "-- finished programming --" )
	logscr.refresh()

def testMemoryBlock(nRange, logscr, stdscr):
	global clkpulses
	logscr.scrollok(True)
	logscr.scroll(1)
	setDataByte(234) #ea / nop
	
	pos = 0
	while pos < nRange:  # when the cpu clock makes a transition, make sure the NOP is enabled
		clkpulses = clkpulses + 1
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)  # A-run mode
		readMonitor(logscr, stdscr)  
		GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH) #B = program mode
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		
		clkpulses = clkpulses + 1
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		pos = pos + 1
		
	GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
	GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)  # A-run mode
	logscr.scroll(1)
	logscr.addstr(19, 1, "-- finished scan --" )
	logscr.refresh()
	
def pulseROMWE(logscr, stdscr):
	GPIO.output(PIN_ROM_WE, GPIO.LOW) # pulse write enable to store data
	readMonitor(logscr, stdscr)
	GPIO.output(PIN_ROM_WE, GPIO.HIGH)
	sleep(0.1)
		
	
wrapper(main)	
GPIO.cleanup()