# Code for REAP Interface (Rotary Encoder Analog Potentiometer) 
# on the CPX for TouchDesigner


# //// IMPORT THE SHIT
import time
import board
import neopixel
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import rotaryio




# //// SETUP THE BOARD
# external analog potentiometer
analogin = AnalogIn(board.A1)

# switch on the external potentiometer
switch = DigitalInOut(board.A2)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# external rotary encoder
encoder = rotaryio.IncrementalEncoder(board.A6, board.A7)

# on board button
button = DigitalInOut(board.BUTTON_B)
button.direction = Direction.INPUT
button.pull = Pull.DOWN

# on board LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# on board neopixels
# neopixel.NeoPixel(pin, number, brightness, display)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0)




# //// DECLARE CONSTANTS
# color constants
WHITE = (255, 255, 255)
RED = 0x100000  # (0x10, 0, 0) also works
YELLOW = (0x10, 0x10, 0)
GREEN = (0, 0x10, 0)
AQUA = (0, 0x10, 0x10)
BLUE = (0, 0, 0x10)
PURPLE = (0x10, 0, 0x10)
BLACK = (0, 0, 0)

# for analog helper
volts = 3.3
brightness_helper_value = 255 




# //// PURE FUNCTIONS
# helpers for getting usable values from the analoginput
def getValue(pin):  # helper to normalizes a 0-1 float from analog input
	#
	return (pin.value) / 65536

def getVoltage(pin):  # helper to get a voltage reading from analog input
	#
	return (pin.value * volts) / 65536

def getBright(pin):  # helper to set RGB value from analog input
	#
	return (pin.value) * brightness_helper_value / 65536

''' ''' 
def switchIsOn():  # inverts PullUP switch to return actual intuitive reading
	#
	return not switch.value




# //// COMMAND / OTHER FUNCTIONS
def doSerialUpdate():  # prints serial messages to console / for output
	# print(serial_message_button, "/", serial_message_encoder)
	# print(serial_message_analog, "/", serial_message_switch)
	print(
		"Button: %d" % serial_message_button,
		"/", 
		"Encoder: %d" % serial_message_encoder,
		"/",
		"Analog: %f" % serial_message_analog,
		"/", 
		"Switch: %d" % serial_message_switch
		)

''' ''' 
def encoderHasChanged():  # updates the encoder position value (and value for serial message)
	global last_encoded_position
	global serial_message_encoder

	global encoder_has_changed
	current_encoded_position = encoder.position

	if last_encoded_position is None or current_encoded_position != last_encoded_position:
		encoder_has_changed = True
		serial_message_encoder = current_encoded_position
		# doSerialUpdate()
	else:
		encoder_has_changed = False

	last_encoded_position = current_encoded_position

def buttonHasChanged():  # updates the button state (and value for serial message)
	global button_state
	global serial_message_button

	global button_has_changed
	pressed = button.value

	if button_state is None or pressed != button_state:
		button_has_changed = True
		# doSerialUpdate()  # the above variable means this can be moved to the main loop

		if pressed:
			serial_message_button = 1
		else:
			serial_message_button = 0
	else:
		button_has_changed = False
	button_state = pressed

	# return button_has_changed
	# return not button.value

def switchHasChanged():  # checks if the switch has changed
	'''
	unfortunately this doesnt really give me the results I'm after...
	'''
	global switch_state
	global serial_message_switch

	if switchIsOn() is not switch_state:
		if switchIsOn():
			val = "ON"
			sval = 1
		else: 
			val = "OFF"
			sval = 0

		serial_message_switch = ("Switch: %d" % sval)
		print("\n switchIsOn /", val, "\n")

		switch_state = switchIsOn()




# //// VARIABLES
# old variables initially setup with the board, now unsure of names and placement
last_encoded_position = None  # MOVE ME
button_state = None  # button.value - MOVE ME
switch_state = None  # not switch.value  # MOVE ME

# new variables
current_switch_state = switchIsOn()
button_has_changed = None
encoder_has_changed = None

# for formatting serial messages
serial_message_encoder = None
serial_message_button = button.value
serial_message_analog = 0
serial_message_switch = switchIsOn()




# //// INITIAL UPDATES
pixels.fill(WHITE)  # set neopixels white 
print("\n CPX Initialized \n ... \n ... \n ...")  # initial formatting message




# //// MAIN LOOP
while True:

	# INITIAL SETUP
	# sets up state tracking for the analog pot switch
	old_switch_state = current_switch_state
	current_switch_state = switchIsOn()
	switch_state_has_changed = current_switch_state != old_switch_state


	# COMMANDS 
	if switch_state_has_changed:
		led.value = switchIsOn()

		if switchIsOn():
			serial_message_switch = 1

		elif not switchIsOn():
			serial_message_analog = 0
			serial_message_switch = 0
			doSerialUpdate()			

	if button_has_changed:  
		doSerialUpdate()

	if encoder_has_changed:
		doSerialUpdate()


	# CONTINUOUS UPDATES
	encoderHasChanged()
	buttonHasChanged()
	# switchHasChanged()

	if switchIsOn():
		analog_value = getValue(analogin)
		serial_message_analog = analog_value

		pixels.brightness = analog_value  # set the CPX pixels brightness
		doSerialUpdate()

	time.sleep(0.05)