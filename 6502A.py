import curses
from curses import wrapper
import RPi.GPIO as GPIO
from time import sleep
import fileinput

hexdump = "xx"
lastaddress = 0
newaddress = 0
clkpulses = 0
PIN_RESET = 8
PIN_6502CLK_PULSE = 17
PIN_MONITOR_IN = 20
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
GPIO.setup(PIN_MONITOR_IN, GPIO.IN)
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
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.cbreak()
	curses.flash()
	curses.noecho()
	stdscr.addstr(1, 1, "r-Reset")
	stdscr.addstr(2, 1, "p-Pulse CPU clock")
	stdscr.addstr(3, 1, "l-Pulse LED")
	#stdscr.addstr(4, 1, "y-Latch on")
	#stdscr.addstr(5, 1, "u-Latch off")
	#stdscr.addstr(6, 1, "i-Serial Input")
	stdscr.addstr(7, 1, "d-Set Data Byte:")
	stdscr.addstr(8, 1, "h-Toggle Data 245 OE")
	stdscr.addstr(9, 1, "f-File input")
	stdscr.addstr(10, 1, "w-Write 6502hexdump.txt")
	stdscr.addstr(11, 1, "q-Write file:")
	stdscr.addstr(12, 1, "s-Step one CPU clock")
	stdscr.addstr(13, 1, "t-Test/Read block")
	stdscr.addstr(21, 1, "X-Exit------------------------------------------------------------------------")
	logscr = curses.newwin(20, 50, 1, 30)
	clkpulses = 0
	flagPINLED = GPIO.LOW
	GPIO.output(PIN_LED, flagPINLED)
	while 1 == 1:
		stdscr.addstr(20, 0,"?")
		curses.echo()
		stdscr.refresh()
		k = stdscr.getch(20, 1)
		stdscr.addstr(20, 5, "[" + str(k) + "]")
		if (k == 114 or k == 82):
			setDataByte(0)
			GPIO.output(PIN_D245_OE, GPIO.HIGH) # go into program mode
			GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH)
			stdscr.addstr(1, 1, "r-Reset?              ")
			sStartAddress = stdscr.getstr(1, 10, 4).decode(encoding="utf-8")
			stdscr.addstr(1, 1, "r-Reset:")
			logscr.scrollok(True)
			logscr.scroll(1)
			logscr.refresh()
			stdscr.refresh()
			sleep(0.2) 
			clkpulses = 0
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)  # should be low already, but just in case.
			stdscr.addstr(2, 1, "p-Pulse CPU clock:" + str(clkpulses))
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
			sleep(0.2)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1..2..3..4")
			logscr.refresh()
			sleep(0.2)
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
				readMonitor(logscr)
				sleep(0.5)
				x = x + 1

			clkpulses = clkpulses + 1
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			readMonitor(logscr)
			sleep(0.2)
			
			intDataHEX = int(sStartAddress[0:2],16)
			setDataByte(intDataHEX)
			GPIO.output(PIN_D245_OE, GPIO.HIGH)
			readMonitor(logscr)
			clkpulses = clkpulses + 1
			GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
			readMonitor(logscr)
			GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
			GPIO.output(PIN_D245_OE, GPIO.LOW)
			GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)
			readMonitor(logscr)
			stdscr.addstr(1, 1, "r-Reset:")
			stdscr.addstr(2, 1, "p-Pulse CPU clock:         ")
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
				readMonitor(logscr)
				lastaddress = newaddress
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 Disable
				GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) # 'A' = run mode, enables RAM OE
				readMonitor(logscr)
				#GPIO.output(PIN_ROM_OE, GPIO.HIGH) #output rom disable
				lastaddress = newaddress

		elif k == 115: # s-Step
				GPIO.output(PIN_D245_OE, GPIO.LOW) # Output 245 disable
				GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW) #A-run
				clkpulses = clkpulses + 1
				stdscr.addstr(2,1,"p-Pulse CPU clock:" + str(clkpulses))
				GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)
				readMonitor(logscr)
				GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)
				readMonitor(logscr)
				lastaddress = newaddress

		elif k == 108: # l-Pulse
				flagPINLED = GPIO.LOW if flagPINLED == GPIO.HIGH else GPIO.HIGH
				GPIO.output(PIN_LED, flagPINLED)
		elif k == 105:
				readMonitor(logscr)
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
			writeToMemory(logscr)
			
		elif k == 113: #q- ask for ML file then write
			stdscr.addstr(11, 1, "q-Write file?                 ")
			sFileName = stdscr.getstr(11, 14, 20).decode(encoding="utf-8")
			readFile(sFileName)
			writeToMemory(logscr)
			stdscr.addstr(11, 1, "q-Write file:")
			
		elif k == 116: # t-Test/Read
			testMemoryBlock(6, logscr)
			
	print("exiting...")
	stdscr.getkey()
	curses.flash()

def readMonitor(logscr):
	global lastaddress
	global newaddress
	global clkpulses
	addrbyte1 = 0
	addrbyte2 = 0
	logscr.scrollok(True)
	logscr.scroll(1)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
	databyte = readMonitor8bits()
	logscr.addstr(19, 1, "[#" + str(clkpulses) + "] flags:" )
	logscr.addstr(19, 13, "r" if databyte & 1 else "W")
	logscr.addstr(19, 14, "H" if databyte & 16 else "L")
	logscr.addstr(19, 15, "P" if databyte & 128 else "R")
	
	databyte = readMonitor8bits()
	logscr.addstr(19, 22, ' data:' + (hex(databyte)[2:4] if databyte > 15 else "0" + hex(databyte)[2:4]))

	addrbyte1 = readMonitor8bits()
	logscr.addstr(19, 31, 'addr:' + (hex(addrbyte1)[2:4] if addrbyte1 > 15 else "0" + hex(addrbyte1)[2:4]))

	addrbyte2 = readMonitor8bits()
	logscr.addstr(19, 38, hex(addrbyte2)[2:4] if addrbyte2 > 15 else "0" + hex(addrbyte2)[2:4])
	
	newaddress = addrbyte1 * 256 + addrbyte2
	if newaddress != lastaddress:
		logscr.addstr(19, 40, " *")
		
	logscr.refresh()
	
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
	with fileinput.input(files=(sFileName)) as f:
		for line in f:
			processLine(line.replace(" ", ""))
			
def processLine(line):
	global hexdump
	hexdump = hexdump + line.strip()

def writeToMemory(logscr):
	global hexdump
	global clkpulses
	logscr.scrollok(True)
	logscr.scroll(1)
	GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH) #B = program mode
	readMonitor(logscr)
	pos = 0
	while hexdump[pos:pos+2] != "xx":
		bb = int(hexdump[pos:pos+2], 16)
		setDataByte(bb)
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		pulseROMWE(logscr)
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		setDataByte(234) #ea / nop
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		sleep(0.01)
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		sleep(0.01)
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
		sleep(0.01)
		GPIO.output(PIN_6502CLK_PULSE, GPIO.LOW)	
		
		logscr.refresh()
		sleep(0.01)
		pos = pos + 2
		
	GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)  # A-run mode
	logscr.scroll(1)
	logscr.addstr(19, 1, "-- finished programming --" )
	logscr.refresh()

def testMemoryBlock(nRange, logscr):
	global clkpulses
	logscr.scrollok(True)
	logscr.scroll(1)
	setDataByte(234) #ea / nop
	
	pos = 0
	while pos < nRange:  # when the cpu clock makes a transition, make sure the NOP is enabled
		GPIO.output(PIN_D245_OE, GPIO.LOW) # Output disable
		GPIO.output(PIN_RUN_PROGRAM, GPIO.LOW)  # A-run mode
		readMonitor(logscr)  
		GPIO.output(PIN_RUN_PROGRAM, GPIO.HIGH) #B = program mode
		GPIO.output(PIN_D245_OE, GPIO.HIGH) # Output Enable
		
		clkpulses = clkpulses + 1
		GPIO.output(PIN_6502CLK_PULSE, GPIO.HIGH)	
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
	
def pulseROMWE(logscr):
	GPIO.output(PIN_ROM_WE, GPIO.LOW) # pulse write enable to store data
	readMonitor(logscr)
	GPIO.output(PIN_ROM_WE, GPIO.HIGH)
	sleep(0.1)
		
	
wrapper(main)	
GPIO.cleanup()