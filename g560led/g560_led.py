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

import logging

from .errors import *
from binascii import unhexlify
from colors import Color, convert_color
from sys import argv, exit as sys_exit
from usb.core import find
from usb.util import claim_interface, release_interface


class LogiBase(object):
	def __init__(self, logger=None):
		self._logger = logger if logger is not None else logging.getLogger(__name__)
		self.device = None
		self.wIndex = None

	@property
	def default_brightness(self) -> int:
		return 100

	@property
	def default_rate(self) -> int:
		return 10_000

	@property
	def logger(self) -> logging.Logger:
		return self._logger

	@logger.setter
	def logger(self, logger:logging.Logger):
		if not isinstance(logger, logging.Logger):
			raise ValueError("The logger must be a logging.Logger object.")
		self._logger = logger

	def process_rate(self, rate):
		if not rate:
			rate = self.default_rate
		try:
			return f"{max(100, min(65535, int(rate))):04x}"
		except ValueError:
			raise ValueError("Invalid rate specified.")

	def process_brightness(self, brightness):
		if not brightness:
			brightness = self.default_brightness
		try:
			return f"{max(1, min(100, int(brightness))):02x}"
		except ValueError:
			raise ValueError("Invalid brightness specified.")

	@staticmethod
	def process_color(color):
		return convert_color(color).rgb.replace("#", "")  # TODO: Check if this can be RGBA instead of RGB

	def send_command(self, data):
		self.attach_mouse()
		self.device.ctrl_transfer(0x21, 0x09, 0x0211, self.wIndex, unhexlify(data))
		self.detach_mouse()

	def attach_mouse(self):
		for product_id, product_title in compatible_devices.items():
			self.device = find(idVendor=vendor_id, idProduct=product_id)
			if self.device is not None:
				# print("Found {}".format(product_title))
				break

		if self.device is None:
			raise NoCompatibleDeviceError('No compatible devices found.')

		self.wIndex = 0x02
		if self.device.is_kernel_driver_active(self.wIndex) is True:
			self.device.detach_kernel_driver(self.wIndex)
			claim_interface(self.device, wself.Index)

	def detach_mouse(self):
		if self.wIndex is None:
			return
		release_interface(self.device, self.wIndex)
		self.device.attach_kernel_driver(self.wIndex)
		self.device = None
		self.wIndex = None


class G560(LogiBase):
	vendor_id = 0x046d # Logitech

	compatible_devices = {
		# 0xc083: "G403 Legacy Mouse",
		# 0xc08f: "G403 HERO Gaming Mouse",
		0x0a78: "G560 Gaming Speaker"
	}

	def __init__(self, logger=None):
		super().__init__(logger=logger)

	@staticmethod
	def help():
		print("""Logitech G403 Mouse LED control
	
	Usage:
	\tg403-led solid {color} - Solid color mode
	\tg403-led cycle [{rate} [{brightness}]] - Cycle through all colors
	\tg403-led breathe {color} [{rate} [{brightness}]] - Single color breathing
	\tg403-led intro {on|off} - Enable/disable startup effect
	
	Arguments:
	\tColor: RRGGBB (RGB hex value)
	\tRate: 100-60000 (Number of milliseconds. Default: 10000ms)
	\tBrightness: 0-100 (Percentage. Default: 100%)""")

	def set_led_solid(self, color):
		if not color:
			raise ValueError("No color option given for setting the solid LED color.")
		color = self.process_color(color)
		return self.set_led('01', f'{color}0000000000')

	def set_led_breathe(self, color, rate, brightness):
		color = self.process_color(color)
		rate = self.process_rate(rate),
		brightness = self.process_brightness(brightness)

		return self.set_led('04', f"{color}{rate}00{brightness}00")
		# return self.set_led('04', color + rate + '00' + brightness + '00')

	def set_led_cycle(self, rate, brightness):
		rate = self.process_rate(rate),
		brightness = self.process_brightness(brightness)

		self.logger.info(f"Cycle info: Rate={rate}\tBrightness={brightness}", extra={"rate": rate, "brightness": brightness})	# TODO: Check how extra works
		return self.set_led('02', f"0000000000{rate}{brightness}")

	def set_led(self, mode, data):
		prefix = '11ff043a'
		left_secondary = '00'
		right_secondary = '01'
		left_primary = '02'
		right_primary = '03'

		suffix = '000000000000'
		self.send_command(prefix + left_secondary + mode + data + suffix)
		self.send_command(prefix + right_secondary + mode + data + suffix)
		self.send_command(prefix + left_primary + mode + data + suffix)
		self.send_command(prefix + right_primary + mode + data + suffix)

	def set_intro_effect(self, arg):
		if arg == 'on' or arg == '1':
			toggle = '01'
		elif arg == 'off' or arg == '0':
			toggle = '02'
		else:
			raise ValueError('Invalid value.')

		self.send_command(f'11ff043a0001{toggle}00000000000000000000000000')


def main(args=None, **kwargs):
	from .tools import set_loger_config

	set_loger_config()
	logger = logging.getLogger(__name__)
	led = G560(logger)

	if args is None:
		args = argv
	if (len(args) < 2):
		led.help()
		sys_exit()

	args = args + [None] * (5 - len(args))

	match (args[1]):
		case "solid":
			g560.set_led_solid(args[2])
		case "cycle":
			g560.set_led_cycle(args[2], args[3])
		case "breathe":
			g560.set_led_breathe(args[2], args[3], args[4])
		case "intro":
			g560.set_intro_effect(args[2])
		case _:
			UnknownLEDModeError(args[1])


if __name__ == '__main__':
	main()
