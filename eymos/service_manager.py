import os
import sys
import json
import logging
import warnings
import platform
from pynput import keyboard

from .logger import LoggerManager, log
from .service import Service


class ServiceManager:

	def __init__(self, config=None, services=None):
		"""Initialize the service manager.
		Args:
			config (dict, optional): The system configuration. Defaults to None.
			services (dict, optional): The services to use. Defaults to None.
		"""
		# Set a default configuration and services
		if config is None:
			config = {}
		if services is None:
			services = {}

		# Set the services
		self._services = services

		# Set the configuration
		self._config = self.set_config(config)

		# Initialize stop queue
		self.stop_queue = []

		# Listen if the escape key is pressed
		if self._config['escape']:
			listener = keyboard.Listener(on_press=self.__on_press)
			listener.start()

		# Hide logs
		logging.getLogger('tensorflow').setLevel(logging.ERROR)
		logging.getLogger('absl').setLevel(logging.ERROR)
		logging.getLogger('cv2').setLevel(logging.ERROR)
		logging.getLogger('PIL').setLevel(logging.ERROR)
		logging.getLogger('matplotlib').setLevel(logging.ERROR)
		logging.getLogger('urllib3').setLevel(logging.ERROR)
		logging.getLogger('requests').setLevel(logging.ERROR)

		# Hide warnings
		warnings.filterwarnings("ignore", category=UserWarning)

	def add(self, name: str, service: type[Service]):
		"""Add a service to the manager.
		Args:
			name (str): The name of the service.
			service (Service): The service to add.
		Returns:
			Any: The service.
		"""
		# Check if the service exists
		if name in self._services:
			raise ValueError(f'The service {name} already exists.')

		# Initialize the service
		service = service(name, self._config, self._services)

		# Set the manager
		service._manager = self

		# Add the service
		self._services[name] = service

		# Return the service
		return service

	def get(self, name: str) -> Service:
		"""Get a service from the manager.
		Args:
			name (str): The name of the service.
		Returns:
			Service: The service.
		"""
		# Check if the service exists
		if name not in self._services:
			raise ValueError(f'The service {name} does not exist.')

		# Get the service
		return self._services[name]

	def get_services(self) -> dict:
		"""Get all services.
		Returns:
			dict: The services.
		"""
		return self._services

	def start(self):
		"""Start all services (in order)."""
		# Check if there are services
		if len(self._services) == 0:
			return

		# Start the first service (automatically starts the others)
		log('Starting the services...')
		first = list(self._services.keys())[0]
		self._services[first].start()

	def stop(self):
		"""Stop all services (in order)."""
		# Check if there are services
		if len(self._services) == 0:
			return

		# Stop all services
		log('Stopping the services...')
		for name in self._services:
			self._services[name].stop()

		# Call the stop queue
		for callback in self.stop_queue:

			# Call the callback
			callback()

		# Clear the stop queue
		self.stop_queue.clear()

	def on_stop(self, callback: callable):
		"""Add a callback to call when the services are stopped.
		Args:
			callback (callable): The callback to call.
		"""
		self.stop_queue.append(callback)

	def restart(self):
		"""Restart all services (in order)."""
		# Stop all services
		self.stop()

		# Start all services
		self.start()

	def reboot(self, system: bool = False):
		"""Reboot the system.
		Args:
			system (bool, optional): Reboot the system. Defaults to False.
		"""
		# Restart the services
		if not system:
			self.restart()
			return

		# Reboot the system
		if platform.system() == 'Windows':
			os.system('shutdown /r /t 1')
		else:
			os.system('reboot')

	def exit(self):
		"""Exit the system."""
		# Stop all services
		self.stop()

		# Exit the system
		log('Exiting the system...')
		sys.exit()

	def set_config(self, config: dict):
		"""Load the configuration.
		Args:
			config (dict): The configuration to load.
		Returns:
			dict: The loaded configuration.
		"""
		# Complete the configuration
		if ('system' not in config) or (type(config['system']) is not dict):
			config['system'] = {}
		if ('debug' not in config['system']) or (type(config['system']['debug']) is not bool):
			config['system']['debug'] = False
		if ('logging' not in config) or (type(config['logging']) is not dict):
			config['logging'] = {}
		if ('level' not in config['logging']) or (type(config['logging']['level']) is not str):
			config['logging']['level'] = logging.INFO
		if ('format' not in config['logging']) or (type(config['logging']['format']) is not str):
			config['logging']['format'] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
		if ('enable' not in config['logging']) or (type(config['logging']['enable']) is not bool):
			config['logging']['enable'] = True
		if ('escape' not in config) or (type(config['escape']) is not bool):
			config['escape'] = True

		# Set the configuration
		self._config = config

		# Refresh the logging configuration
		self.__update_logging()

		# Return the configuration
		return self._config

	def set_config_file(self, file: str):
		"""Load the configuration from a file.
		Args:
			file (str): The file to load.
		Returns:
			dict: The loaded configuration.
		"""
		# Load the configuration from the file
		if not os.path.exists(file):
			raise FileNotFoundError(f'The configuration file {file} does not exist.')
		with open(file, 'r') as f:
			config = json.load(f)

		# Set the configuration
		return self.set_config(config)

	def __on_press(self, key):
		"""Listen if the escape key is pressed.
		Args:
			key (keyboard.Key): The key pressed.
		"""
		if key == keyboard.Key.esc:
			self.exit()

	def __update_logging(self):
		"""Update the logging configuration."""
		# Disable logging in LoggingManager
		if not self._config['logging']['enable']:
			LoggerManager.disable()
			return

		# Enable logging in LoggingManager
		LoggerManager.enable(self._config['logging']['level'], self._config['logging']['format'])