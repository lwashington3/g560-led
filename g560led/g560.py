#!/usr/bin/python3.11

#
# Logitech Mouse LED control
#
#  * G403 Prodigy Mouse
#  * G403 HERO Gaming Mouse
#
# https://github.com/stelcheck/g403-led
# Author: Smasty, hello@smasty.net
# Licensed under the MIT license.

from sys import exit as sys_exit
from .logi import *


__ALL__ = ["G560", "main"]


class G560(LogiBase):
	def __init__(self, logger=None):
		super().__init__(logger=logger)

	@staticmethod
	def help():
		print("""Logitech G560 Gaming Speakers control
	
	Usage:
	\tg560 solid {color} - Solid color mode
	\tg560 cycle [{rate} [{brightness}]] - Cycle through all colors
	\tg560 breathe {color} [{rate} [{brightness}]] - Single color breathing
	\tg560 intro {on|off} - Enable/disable startup effect
	
	Arguments:
	\tColor: RRGGBB (RGB hex value)
	\tRate: 100-60000 (Number of milliseconds. Default: 10000ms)
	\tBrightness: 0-100 (Percentage. Default: 100%)""")

	@property
	def compatible_devices(self) -> dict[int, str]:
		return {
			0x0a78: "G560 Gaming Speaker"
		}

	@property
	def default_wIndex(self) -> int:
		return 0x02

	def set_led_solid(self, color):
		if not color:
			raise ValueError("No color option given for setting the solid LED color.")
		color = self.process_color(color)
		return self.set_led(LEDMode.Solid, f'{color}0000000000')

	def set_led_breathe(self, color, rate, brightness):
		color = self.process_color(color)
		rate = self.process_rate(rate)
		brightness = self.process_brightness(brightness)

		return self.set_led(LEDMode.G560_Breathe, f"{color}{rate}00{brightness}00")

	def set_led_cycle(self, rate, brightness):
		rate = self.process_rate(rate)
		brightness = self.process_brightness(brightness)

		self.logger.info(f"Cycle info: Rate={rate}\tBrightness={brightness}", extra={"rate": rate, "brightness": brightness})
		return self.set_led(LEDMode.Cycle, f"0000000000{rate}{brightness}")

	def set_led(self, mode:LEDMode, data):
		prefix = '11ff043a'
		suffix = '000000000000'

		for speaker in SpeakerLocation:
			self.send_command(f"{prefix}{speaker.value}{mode}{data}{suffix}")

	def set_intro_effect(self, arg):
		if arg == 'on' or arg == '1':
			toggle = '01'
		elif arg == 'off' or arg == '0':
			toggle = '02'
		else:
			raise ValueError('Invalid value.')

		self.send_command(f'11ff043a0001{toggle}00000000000000000000000000')


def main(args=None):
	from .tools import set_loger_config
	from .errors import UnknownLEDModeError
	import logging

	set_loger_config()
	logger = logging.getLogger(__name__)
	led = G560(logger)

	if args is None:
		from sys import argv
		args = argv
	if (len(args) < 2):
		led.help()
		sys_exit()

	args = args + [None] * (5 - len(args))

	match (args[1]):
		case "solid":
			led.set_led_solid(args[2])
		case "cycle":
			led.set_led_cycle(args[2], args[3])
		case "breathe":
			led.set_led_breathe(args[2], args[3], args[4])
		case "intro":
			led.set_intro_effect(args[2])
		case _:
			raise UnknownLEDModeError(args[1])


if __name__ == '__main__':
	main()
