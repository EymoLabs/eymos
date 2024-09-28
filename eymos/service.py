import abc
import time
import logging
import threading

from .logger import log


class Service(metaclass=abc.ABCMeta):
	DEPENDENCIES = []
	MAX_ERRORS = 5
	MAX_ERRORS_REBOOT = -1
	ERROR_INTERVAL = 5
	LOOP_DELAY = 0.25

	def __init__(self, name: str, config: dict, services: dict):
		"""Initialize the service.
		Args:
			name (str): The name of the service.
			config (dict): The system configuration.
			services (dict, optional): The services to use. Defaults to {}.
		"""
		# Check if the service exists
		if name in services:
			raise ValueError(f'The service {name} already exists.')

		# Set a default configuration and services
		if config is None:
			config = {}
		if services is None:
			services = {}

		# Service information
		self._name = name
		self._global_config = config
		self._config = config[name] if name in config else {}
		self._services = services
		self._manager = None
		self._loop_delay = self.LOOP_DELAY

		# Service status
		self.__initialized = False
		self.__init_try = 0
		self.__errors = 0

		# Service thread
		self.__thread = None
		self.__thread_stop_event = threading.Event()

		# Set the service
		services[name] = self

	@abc.abstractmethod
	def init(self):
		"""Initialize the service."""
		raise NotImplementedError('The init method must be implemented.')

	@abc.abstractmethod
	def destroy(self):
		"""Destroy the service."""
		raise NotImplementedError('The destroy method must be implemented.')

	def start(self):
		"""Start the service."""

		# Check if the service has been initialized
		if self.__initialized:
			return

		# Check if all dependencies are initialized
		for dependency in self.DEPENDENCIES:
			if dependency not in self._services:
				raise ValueError(f'The service {self._name} requires the service {dependency}.')
			if not self._services[dependency].is_initialized():
				log(f'The {self._name} service is waiting for the {dependency} service to start...')
				self.__start_other_service()
				return

		# Initialize the service
		log(f'Starting the {self._name} service...')
		self.init()

		# Call the thread method
		if hasattr(self, 'before') or hasattr(self, 'loop'):
			self.__thread_stop_event.clear()
			self.__thread = threading.Thread(target=self.__thread_execution)
			self.__thread.start()

		# Set the service as initialized
		self.__initialized = True
		log(f'The {self._name} service has started successfully.')

		# Start other services
		services = {k: v for k, v in self._services.items() if not v.is_initialized()}
		if services:
			self.__start_other_service()

	def stop(self):
		"""Stop the service."""
		log(f'Stopping the {self._name} service...')
		if self.__thread:
			self.__thread_stop_event.set()
			if threading.current_thread() != self.__thread:
				self.__thread.join()
		self.destroy()
		self.__initialized = False
		self.__init_try = 0
		log(f'The {self._name} service has stopped successfully.')

	def is_initialized(self) -> bool:
		"""Check if the service has been initialized.
		Returns:
			bool: True if the service has been initialized, False otherwise.
		"""
		return self.__initialized

	def __reboot(self):
		"""Reboot the robot for Linux systems, stop all services and start the service again for other systems."""
		log('Stopping all services...')
		for service in self._services.values():
			service.stop()
		log('All services have been stopped.')
		self.start()

	def __start_other_service(self):
		"""Start another service by try priority."""
		services = {k: v for k, v in self._services.items() if not v.is_initialized()}
		services = dict(sorted(services.items(), key=lambda item: item[1].__init_try))
		service = list(services.values())[0]
		self.__init_try += 1
		service.start()

	def __thread_execution(self):
		"""Service thread execution."""
		# Call the before method
		if hasattr(self, 'before'):
			self.before()

		# Call the loop method
		if hasattr(self, 'loop'):
			if self._global_config.get('system', {}).get('debug', True):
				while not self.__thread_stop_event.is_set():
					self.loop()
					if self.__thread_stop_event.wait(self._loop_delay):
						break
			else:
				while True:
					try:
						self.loop()
						if self.__thread_stop_event.wait(self._loop_delay):
							break
					except KeyboardInterrupt:
						break
					except Exception as e:
						self.__errors += 1
						log(f'An error occurred in the {self._name} service thread: {e}', logging.ERROR)
						if self.MAX_ERRORS_REBOOT != -1 and self.__errors >= self.MAX_ERRORS_REBOOT:
							log(f'The {self._name} service has reached the maximum number of errors. Rebooting the robot...', logging.ERROR)
							self.__reboot()
							break
						if self.MAX_ERRORS != -1 and self.__errors >= self.MAX_ERRORS:
							log(f'The {self._name} service has reached the maximum number of errors. Stopping the service...', logging.ERROR)
							break
						time.sleep(self.ERROR_INTERVAL)
