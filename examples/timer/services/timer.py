from eymos import Service, log


class TimerService(Service):
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
			self.__is_running = False
			log("Timer stopped")
		else:
			log(f"Time left: {self.__time}")

	# Add more custom methods if needed
	def start_timer(self, time):
		self.__time = min(time, self.__max_time)
		self.__is_running = True
		log("Timer started")

	def stop_timer(self):
		self.__is_running = False
		self.__time = 0
		log("Timer stopped")

	def get_time(self):
		return self.__time
