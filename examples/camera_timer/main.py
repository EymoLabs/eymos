import time

from eymos.service_manager import ServiceManager
from eymos.services.camera import CameraService
from services.camera_timer import CameraTimerService


def main():
	# Create a new service manager
	service_manager = ServiceManager()

	# Link a configuration to the service manager
	service_manager.set_config_file("config.json")

	# Add the services to the manager
	timer = service_manager.add("timer", CameraTimerService)
	camera = service_manager.add("camera", CameraService)

	# Initialize the services
	service_manager.start()  # Start the first service added, and then the rest

	# Start the timer to take a picture in 3 seconds
	timer.take_photo(3)


if __name__ == "__main__":
	main()