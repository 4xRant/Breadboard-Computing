import curses
from curses import wrapper
import RPi.GPIO as GPIO
from time import sleep
PIN_PULSE = 12
PIN_LED = 21
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
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LED, GPIO.OUT)
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
	flagPINLED = GPIO.HIGH
	GPIO.output(PIN_LED, flagPINLED)
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
	stdscr.addstr(8, 1, "d-Toggle Data OE")
	stdscr.addstr(12, 1, "X-Exit")
	clkpulses = 0
	while 1 == 1:
		stdscr.addstr(20,0,"?")
		curses.echo()
		stdscr.refresh()
		k = stdscr.getch(20,1)
		stdscr.addstr(20,5, "[   ]")
		stdscr.addstr(20,6, str(k))
		if (k == 114 or k == 82):
			stdscr.addstr(1,1,"r-Reset", curses.color_pair(1))
		elif k == 88:
				break
		elif k == 80 or k == 112:
				clkpulses = clkpulses + 1
				stdscr.addstr(2,1,"p-Pulse CPU clock:" + str(clkpulses))
				GPIO.output(PIN_PULSE, GPIO.HIGH)
				GPIO.output(PIN_PULSE, GPIO.LOW)
				readMonitor(stdscr)
		elif k == 76 or k == 108:
				flagPINLED = GPIO.LOW if flagPINLED == GPIO.HIGH else GPIO.HIGH
				GPIO.output(PIN_LED, flagPINLED)
		elif k == 105:
				readMonitor(stdscr)
		elif k == 117:
				stdscr.addstr(4, 1, "y-Latch on")
				stdscr.addstr(5, 1, "u-Latch OFF")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
		elif k == 121:
				stdscr.addstr(4, 1, "y-Latch ON")
				stdscr.addstr(5, 1, "u-Latch off")
				GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
		elif k == 68:
				GPIO.output(PIN_D1, GPIO.LOW)
				GPIO.output(PIN_D2, GPIO.LOW)
				GPIO.output(PIN_D_OE, GPIO.HIGH)
				sDataHEX = stdscr.getstr(7,18, 2).decode(encoding="utf-8")
				intDataHEX = int(sDataHEX, 16)
		elif k == 100:
				GPIO.output(PIN_D1, GPIO.HIGH if intDataHEX & 1 else GPIO.LOW)
				GPIO.output(PIN_D2, GPIO.HIGH if intDataHEX & 2 else GPIO.LOW)
				GPIO.output(PIN_D3, GPIO.HIGH if intDataHEX & 4 else GPIO.LOW)
				GPIO.output(PIN_D4, GPIO.HIGH if intDataHEX & 8 else GPIO.LOW)
				GPIO.output(PIN_D5, GPIO.HIGH if intDataHEX & 16 else GPIO.LOW)
				GPIO.output(PIN_D6, GPIO.HIGH if intDataHEX & 32 else GPIO.LOW)
				GPIO.output(PIN_D7, GPIO.HIGH if intDataHEX & 64 else GPIO.LOW)
				GPIO.output(PIN_D8, GPIO.HIGH if intDataHEX & 128 else GPIO.LOW)
				GPIO.output(PIN_D_OE, GPIO.LOW)
		else:
			stdscr.addstr(1,1,"r-Reset", curses.color_pair(2))
			
	print("exiting...")
	stdscr.getkey()
	curses.flash()

def readMonitor(stdscr):
	stdscr.addstr(6, 1, "i-Serial Input............................")
	GPIO.output(PIN_MONITOR_LATCH, GPIO.HIGH)
	GPIO.output(PIN_MONITOR_LATCH, GPIO.LOW)
	pinnumber = 0
	databyte = readMonitor8bits()
	stdscr.addstr(6, 1, "i-Serial Input flags:" + hex(databyte)[2:4])

	databyte = readMonitor8bits()
	stdscr.addstr(6, 25, 'data:' + hex(databyte)[2:4])

	databyte = readMonitor8bits()
	stdscr.addstr(6, 34, 'addr:' + hex(databyte)[2:4])

	databyte = readMonitor8bits()
	stdscr.addstr(6, 41, hex(databyte)[2:4] if databyte > 15 else "0" + hex(databyte)[2:4])

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

wrapper(main)	
GPIO.cleanup()