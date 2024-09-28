import cv2
from PIL import Image

from eymos import Service, log
from eymos.services import FrameType


class CameraTimerService(Service):
	DEPENDENCIES = ['camera']
	MAX_TIME = 300
	TIME_INTERVAL = 1

	def __init__(self, name: str, config: dict, services: dict):
		"""Initialize the service.
		Args:
			name (str): The name of the service.
			config (dict): The service configuration.
			services (dict): The services to use.
		"""
		# Initialize the service attributes
		self.__time = None
		self.__is_running = None
		self.__max_time = None

		# Call the parent class constructor
		super().__init__(name, config, services)

	def init(self):
		"""Initialize the service. Required."""
		self.__time = 0
		self.__is_running = False
		self.__max_time = self._config.get("max_time", self.MAX_TIME)
		self._loop_delay = self.TIME_INTERVAL   # Control the loop delay in seconds

	def destroy(self):
		"""Destroy the service. Required."""
		self.__time = None
		self.__is_running = None
		self.__max_time = None

	def loop(self):
		"""Service loop. Optional."""
		if not self.__is_running:
			return
		if self.__time > 0:
			self.__time -= 1
		if self.__time == 0:
			if self.__is_running:
				self.shoot_photo()
				self._manager.exit()
			self.__is_running = False
		else:
			log(f"Time left: {self.__time} seconds")

	# Add more custom methods if needed
	def take_photo(self, time):
		self.__time = min(time, self.__max_time)
		self.__is_running = True
		log(f"Taking a photo in {self.__time} seconds")

	def cancel(self):
		self.__is_running = False
		self.__time = 0
		log("The photo timer has been canceled")

	def get_time(self):
		return self.__time

	def shoot_photo(self):
		"""Take a photo."""
		log("Taking a photo")
		camera_service = self._services.get('camera')
		if camera_service is None:
			log("Camera service not found")
			return
		frame = camera_service.get_frame(FrameType.IMAGE)
		if frame is None:
			log("Could not get the frame")
			return
		try:
			frame.show()
			log("Photo taken")
		except Exception as e:
			log(f"An error occurred while taking a photo: {e}")