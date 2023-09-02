from .errors import *
from abc import abstractmethod, ABC
from binascii import unhexlify
from colors import Color
from enum import StrEnum
import logging
from usb.core import find
from usb.util import claim_interface, release_interface


__ALL__ = ["SpeakerLocation", "LEDMode", "LogiBase"]


class SpeakerLocation(StrEnum):
	Left_Secondary	= '00'
	Right_Secondary = '01'
	Left_Primary	= '02'
	Right_Primary	= '03'


class LEDMode(StrEnum):
	Solid			= "01"
	Cycle			= "02"
	Breathe			= "03"
	G560_Breathe 	= "04"


class LogiBase(ABC):
	def __init__(self, logger=None):
		self._logger = logger if logger is not None else logging.getLogger(__name__)
		self.device = None
		self.wIndex = None

	@property
	@abstractmethod
	def compatible_devices(self) -> dict[int, str]:
		pass

	@property
	@abstractmethod
	def default_wIndex(self) -> int:
		pass

	@property
	def default_brightness(self) -> int:
		return 100

	@property
	def default_rate(self) -> int:
		return 10_000

	@property
	def vendor_id(self) -> int:
		return 0x046d  # Logitech

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
			return '{:04x}'.format(max(100, min(65535, int(rate))))
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
		return Color(rgba=color).rgb.replace("#", "")

	def send_command(self, data):
		self.send_commands([data])

	def send_commands(self, datalist):
		self.attach_mouse()
		for data in datalist:
			self.device.ctrl_transfer(0x21, 0x09, 0x0211, self.wIndex, unhexlify(data))
		self.detach_mouse()

	def attach_mouse(self):
		for product_id, product_title in self.compatible_devices.items():
			self.device = find(idVendor=self.vendor_id, idProduct=product_id)
			if self.device is not None:
				break

		if self.device is None:
			raise NoCompatibleDeviceError(f'No compatible devices found for: {self.vendor_id:04x}: (' + ",".join(self.compatible_devices.keys()) + ").")

		self.wIndex = self.default_wIndex
		if self.device.is_kernel_driver_active(self.wIndex):
			self.device.detach_kernel_driver(self.wIndex)
			claim_interface(self.device, self.wIndex)

	def detach_mouse(self):
		if self.wIndex is None:
			return
		release_interface(self.device, self.wIndex)
		self.device.attach_kernel_driver(self.wIndex)
		self.device = None
		self.wIndex = None
