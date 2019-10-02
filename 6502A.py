import curses
from curses import wrapper
import RPi.GPIO as GPIO
from time import sleep
PIN_RESET = 12
PIN_PULSE = 21
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
PIN_D_OE = 2
PIN_LED = 15
flagPINLED = GPIO.LOW
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RESET, GPIO.OUT)
GPIO.output(PIN_RESET, GPIO.HIGH)
GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.output(PIN_LED, flagPINLED)
GPIO.setup(PIN_PULSE, GPIO.OUT)
GPIO.setup(PIN_MONITOR_IN, GPIO.IN)
GPIO.setup(PIN_MONITOR_CLK, GPIO.OUT)
GPIO.setup(PIN_MONITOR_LATCH, GPIO.OUT)
GPIO.output(PIN_MONITOR_CLK, GPIO.LOW)
GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
GPIO.setup(PIN_D1, GPIO.OUT)
GPIO.setup(PIN_D2, GPIO.OUT)
GPIO.setup(PIN_D3, GPIO.OUT)
GPIO.setup(PIN_D4, GPIO.OUT)
GPIO.setup(PIN_D5, GPIO.OUT)
GPIO.setup(PIN_D6, GPIO.OUT)
GPIO.setup(PIN_D7, GPIO.OUT)
GPIO.setup(PIN_D8, GPIO.OUT)
GPIO.setup(PIN_D_OE, GPIO.OUT)
GPIO.output(PIN_D_OE, GPIO.HIGH) # turn data 245 OE high, so that it is off.

def main(stdscr):
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.cbreak()
	curses.flash()
	curses.noecho()
	stdscr.addstr(1, 1, "r-Reset")
	stdscr.addstr(2, 1, "p-Pulse CPU clock")
	stdscr.addstr(3, 1, "l-Pulse LED")
	stdscr.addstr(4, 1, "y-Latch on")
	stdscr.addstr(5, 1, "u-Latch off")
	stdscr.addstr(6, 1, "i-Serial Input")
	stdscr.addstr(7, 1, "D-Set Data Byte:")
	stdscr.addstr(8, 1, "h-Toggle Data OE high-z")
	stdscr.addstr(12, 1, "X-Exit")
	logscr = curses.newwin(20, 45, 1, 30)
	clkpulses = 0
	flagPINLED = GPIO.LOW
	GPIO.output(PIN_LED, flagPINLED)
	while 1 == 1:
		stdscr.addstr(20, 0,"?")
		curses.echo()
		stdscr.refresh()
		k = stdscr.getch(20, 1)
		stdscr.addstr(20,5, "[" + str(k) + "]")
		if (k == 114 or k == 82):
			GPIO.output(PIN_D_OE, GPIO.LOW)
			stdscr.addstr(1, 1, "r-Reset?         ", curses.color_pair(1))
			sStartAddress = stdscr.getstr(1, 10, 4).decode(encoding="utf-8")
			stdscr.addstr(1, 1, "r-Reset: " + sStartAddress + "     ", curses.color_pair(2))
			logscr.scrollok(True)
			logscr.scroll(1)
			logscr.refresh()
			stdscr.refresh()
			sleep(1) 
			clkpulses = 0
			stdscr.addstr(2, 1, "p-Pulse CPU clock:" + str(clkpulses))
			GPIO.output(PIN_RESET, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW")
			logscr.refresh()
			stdscr.refresh()
			sleep(1)
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1")
			logscr.refresh()
			stdscr.refresh()
			sleep(1)
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			logscr.addstr(19, 1, "RESET LOW PULSE 1, PULSE 2")
			logscr.refresh()
			stdscr.refresh()
			sleep(1)
			GPIO.output(PIN_RESET, GPIO.HIGH)
			logscr.scroll(1)
			logscr.addstr(19, 1, "RESET HIGH")
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 1/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			stdscr.refresh()
			logscr.refresh()
			sleep(1)
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 2/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			logscr.refresh()
			stdscr.refresh()
			sleep(1)
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 3/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)
			stdscr.refresh()
			logscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 4/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)
			stdscr.refresh()
			logscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 5/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)
			stdscr.refresh()
			logscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 6/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)
			stdscr.refresh()
			logscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 7/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)

			intDataHEX = int(sStartAddress[2:4],16)
			writeDataByte(intDataHEX)
			logscr.refresh()
			stdscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 8/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			sleep(1)

			intDataHEX = int(sStartAddress[0:2],16)
			writeDataByte(intDataHEX)
			logscr.refresh()
			clkpulses = clkpulses + 1
			stdscr.addstr(2, 1,"p-Pulse CPU clock: 9/7")
			GPIO.output(PIN_PULSE, GPIO.HIGH)
			GPIO.output(PIN_PULSE, GPIO.LOW)
			readMonitor(logscr, clkpulses)
			stdscr.addstr(1, 1, "r-Reset:  Finished   ", curses.color_pair(1))
			stdscr.addstr(2, 1, "p-Pulse CPU clock:           ")
			stdscr.refresh()
			logscr.refresh()
			sleep(1)
		elif k == 88:
				break
		elif k == 80 or k == 112:
				clkpulses = clkpulses + 1
				stdscr.addstr(2,1,"p-Pulse CPU clock:" + str(clkpulses))
				GPIO.output(PIN_PULSE, GPIO.HIGH)
				GPIO.output(PIN_PULSE, GPIO.LOW)
				readMonitor(logscr, clkpulses)
		elif k == 108: # l-Pulse
				flagPINLED = GPIO.LOW if flagPINLED == GPIO.HIGH else GPIO.HIGH
				GPIO.output(PIN_LED, flagPINLED)
		elif k == 105:
				readMonitor(logscr, clkpulses)
		elif k == 117:
				stdscr.addstr(4, 1, "y-Latch on")
				stdscr.addstr(5, 1, "u-Latch OFF")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
		elif k == 121:
				stdscr.addstr(4, 1, "y-Latch ON")
				stdscr.addstr(5, 1, "u-Latch off")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
		elif k == 68: # D
				GPIO.output(PIN_D_OE, GPIO.LOW)
				stdscr.addstr(7, 1, "D-Set Data Byte?     ")
				sDataHEX = stdscr.getstr(7,18, 2).decode(encoding="utf-8")
				intDataHEX = int(sDataHEX, 16)
				stdscr.addstr(7, 1, "D-Set Data Byte:")
				writeDataByte(intDataHEX)
				stdscr.refresh()
		elif k == 104:  # h
			GPIO.output(PIN_D_OE, GPIO.LOW)
					
	print("exiting...")
	stdscr.getkey()
	curses.flash()

def readMonitor(logscr, clkpulses):
	logscr.scrollok(True)
	logscr.scroll(1)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
	databyte = readMonitor8bits()
	logscr.addstr(19, 1, "[#" + str(clkpulses) + "] Input flags:" + hex(databyte)[2:4])

	databyte = readMonitor8bits()
	logscr.addstr(19, 22, ' data:' + hex(databyte)[2:4])

	databyte = readMonitor8bits()
	logscr.addstr(19, 31, 'addr:' + (hex(databyte)[2:4] if databyte > 15 else "0" + hex(databyte)[2:4]))

	databyte = readMonitor8bits()
	logscr.addstr(19, 38, hex(databyte)[2:4] if databyte > 15 else "0" + hex(databyte)[2:4])
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

def writeDataByte(intDataHEX):
	GPIO.output(PIN_D_OE, GPIO.LOW) # goes through a NAND gate to set OE HIGH (245 no output)
	GPIO.output(PIN_D1, GPIO.HIGH if intDataHEX & 1 else GPIO.LOW)
	GPIO.output(PIN_D2, GPIO.HIGH if intDataHEX & 2 else GPIO.LOW)
	GPIO.output(PIN_D3, GPIO.HIGH if intDataHEX & 4 else GPIO.LOW)
	GPIO.output(PIN_D4, GPIO.HIGH if intDataHEX & 8 else GPIO.LOW)
	GPIO.output(PIN_D5, GPIO.HIGH if intDataHEX & 16 else GPIO.LOW)
	GPIO.output(PIN_D6, GPIO.HIGH if intDataHEX & 32 else GPIO.LOW)
	GPIO.output(PIN_D7, GPIO.HIGH if intDataHEX & 64 else GPIO.LOW)
	GPIO.output(PIN_D8, GPIO.HIGH if intDataHEX & 128 else GPIO.LOW)
	GPIO.output(PIN_D_OE, GPIO.HIGH)

wrapper(main)	
GPIO.cleanup()