import logging


class LoggerManager:
	LEVEL = logging.INFO
	FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	ENABLE = True

	@staticmethod
	def enable(level: int = logging.INFO, message: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
		"""Enable the logging."""
		# Update the logger manager
		LoggerManager.LEVEL = level
		LoggerManager.FORMAT = message
		LoggerManager.ENABLE = True

		# Set the logging level and format
		logging.basicConfig(level=level, format=message)

		# Log the message
		logging.info("Logging enabled")

	@staticmethod
	def disable():
		"""Disable the logging."""
		# Update the logger manager
		LoggerManager.ENABLE = False

		# Log the message
		logging.info("Logging disabled")

	@staticmethod
	def log(message: str, level: int = None):
		"""Log the message.
		Args:
			message (str): The message to log.
			level (int, optional): The logging level. Defaults to logger.LEVEL.
		"""
		# Check if logging is enabled
		if not LoggerManager.ENABLE:
			return

		# Set the logging level if not set
		if not level:
			level = LoggerManager.LEVEL

		# Log the message
		if level == logging.DEBUG:
			logging.debug(message)
		elif level == logging.INFO:
			logging.info(message)
		elif level == logging.WARNING:
			logging.warning(message)
		elif level == logging.ERROR:
			logging.error(message)
		elif level == logging.CRITICAL:
			logging.critical(message)
		else:
			raise ValueError("Invalid logging level")


def log(message: str, level: int = None):
	"""Log the message.
	Args:
		message (str): The message to log.
		level (int, optional): The logging level. Defaults to logger.LEVEL.
	"""
	LoggerManager.log(message, level)
