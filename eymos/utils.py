import os
import platform


# Create a class to store some data used by the utils functions
class UtilsManager:
	RPI_CHIPS = ['BCM2708', 'BCM2709', 'BCM2711', 'BCM2835', 'BCM2836', 'BCM2837', 'BCM2837B0', 'BCM2712', 'RP1']
	DATA = {}


def my_os():
	"""Check which OS is running.
	Returns:
		str: The OS name (Windows, Mac, Rpi, Linux), or None if the OS is not recognized.
	"""
	# Check if os is already defined
	if 'os' in UtilsManager.DATA:
		return UtilsManager.DATA['os']

	# Check if the OS is Windows
	if platform.system() == 'Windows':
		UtilsManager.DATA['os'] = 'Windows'
		return 'Windows'

	# Check if the OS is Mac
	if platform.system() == 'Darwin':
		UtilsManager.DATA['os'] = 'Mac'
		return 'Mac'

	# Check if the OS is Linux
	if platform.system() == 'Linux':

		# Check if the OS is Raspberry Pi
		if os.name == 'posix':
			try:
				with open('/proc/cpuinfo', 'r') as cpuinfo:
					for line in cpuinfo:
						if line.startswith('Hardware'):
							if any([chip in line for chip in UtilsManager.RPI_CHIPS]):
								UtilsManager.DATA['os'] = 'Rpi'
								return 'Rpi'
						if line.startswith('Model'):
							if 'Raspberry Pi' in line:
								UtilsManager.DATA['os'] = 'Rpi'
								return 'Rpi'
			except FileNotFoundError:
				pass

		UtilsManager.DATA['os'] = 'Linux'
		return 'Linux'

	# OS not recognized
	UtilsManager.DATA['os'] = None
	return None
