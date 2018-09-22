# This code is for one single switch pot to be connected...
# if 3 prongs are facing LEFT side of pot...
# pot top to GND
# pot center to A1
# pot bottom to 3.3v
# switchleft to A2
# switchright to GND
# consider makinga fritzing image or schematic...

# Sept 06 2018
# Added External Rotary Encoder and Button B
# Added Serial Message variable and function
# ... for sending to Touch Designer
# NOTE! Using the Analog Pot will break TD data!!!


# //// IMPORT THE SHIT
import time
import board
import neopixel
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import rotaryio


# //// DECLARE VARIABLES AND FUNCTIONS
WHITE = (255, 255, 255)
RED = 0x100000  # (0x10, 0, 0) also works
YELLOW = (0x10, 0x10, 0)
GREEN = (0, 0x10, 0)
AQUA = (0, 0x10, 0x10)
BLUE = (0, 0, 0x10)
PURPLE = (0x10, 0, 0x10)
BLACK = (0, 0, 0)

analogin = AnalogIn(board.A1)

switch = DigitalInOut(board.A2)
switch.direction = Direction.INPUT
switch.pull = Pull.UP
switch_state = not switch.value

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

volts = 3.3
brights = 255 

encoder = rotaryio.IncrementalEncoder(board.A6, board.A7)
last_position = None

button = DigitalInOut(board.BUTTON_B)
button.direction = Direction.INPUT
button.pull = Pull.DOWN
button_state = None  # button.value

# for formatting serial messages
serialmessage_button = None
serialmessage_rotary = None

def serialUpdate():
	print(serialmessage_button, "/", serialmessage_rotary)

def rotary():
	global last_position
	global serialmessage_rotary

	position = encoder.position
	if last_position is None or position != last_position:
		# print("Encoder:", position)
		serialmessage_rotary = "Encoder: %d" % position
		serialUpdate()
	last_position = position

def buttonPress():
	global button_state
	global serialmessage_button
	pressed = button.value

	if button_state is None or pressed != button_state:
		if pressed:
			serialmessage_button = "Button: 1"
			# print(serialmessage_button)			
			# serialUpdate()
		else:
			serialmessage_button = "Button: 0"
			# print(serialmessage_button)
			# serialUpdate()
		serialUpdate()
	button_state = pressed

	# return not button.value


def switched():  # inverts PullUP switch to normalize value
	return not switch.value
	# fold function 

def switchCheck():  # switch state
	global switch_state
	if switched() is not switch_state:
		# print("switchstate changed 01")
		if switched():
			val = "ON"
			print("\n switched /", val, "\n")  # \n is newline
		else: 
			val = "OFF"
			print("\n switched /", val, "\n")
		switch_state = switched()

# // dont really know what to make of the switchCheck above...
# // like I dont know how to put it to good use down in the main loop...
# def switchPulse():  # return a boolean pulse when switched
# 	# time.sleep(1)  # with this line, the switch pulse actually registers in the console
# 	if switched() is not switch_state:
# 		return True
# 	else:
# 		return False


def getVoltage(pin):  # helper to get a voltage reading
	return (pin.value * volts) / 65536
	# fold function

def getValue(pin):  # normalizes a 0-1 float
	return (pin.value) / 65536
	# fold function

def getBright(pin):  # for fading the neopixels color value instead of bright
	return (pin.value) * brights / 65536
	# fold function

# neopixel.NeoPixel(pin, number, brightness, display)
# id found the arguments here confusing, but I'm starting to see it... as above
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=getValue(analogin))
pixels.fill(WHITE)

print("CPX Initialized \n ... \n ... \n ... \n")
# //// DO THE STUFF
while True:

	rotary()
	buttonPress()

	# sets RGB tuple for neopix to analog brightness value
	pixfill = (int(getBright(analogin)), int(getBright(analogin)), int(getBright(analogin)))
	# print('pixfill:', pixfill)

	switchCheck()
	# print("switchPULSE :", switchPulse())

	if switched():
		# print("switch ON")
		# print("Full Value: %f" % getValue(analogin))  # Prints full analog range


		# // each of the following methods have their faults
		# no nice way to get a real smooth fade towards dark values

		# 01 Adjusting Brightness
		pixels.brightness = getValue(analogin) 
			# theres a hard cutoff towards the lower values here.

		# 02 Adjusting COLOR value using fill 
		# pixels.brightness = 1
		# pixels.fill(pixfill)
		# print("pixel value:", pixels[0])
			# color flickering towards lower ends
			# dont forget to set brightness, cause fill alone doesnt cut it!

		# 03 Adjusting COLOR value using a loop over all pixels
		# for i in range(len(pixels)):
		# 	pixels[i] = pixfill
			# runs terribly slow
			# only did this because I thought the above wasnt working

		if pixels.brightness < 0.998:
			print("Value: %f" % getValue(analogin))
			# print()
		else:
			print("FULL BRIGHTNESS!!!")
	else: 
		# print("switch OFF")
		# print("Analog Voltage: %f" % getVoltage(analogin))
		pass

	led.value = switched()
	# led.value = getValue(analogin)  
		# fade RED LED based on value...
		# this needs to be PWM to work... DigitalIO is only binary!!!

	time.sleep(0.05)
