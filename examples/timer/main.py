import time
from eymos.service_manager import ServiceManager
from services.timer import TimerService


def main():
	# Create a new service manager
	service_manager = ServiceManager()

	# Link a configuration to the service manager
	service_manager.set_config_file("config.json")

	# Add the services to the manager
	timer = service_manager.add("timer", TimerService)

	# Initialize the services
	service_manager.start()  # Start the first service added, and then the rest

	# Wait for 1 second
	time.sleep(1)

	# Start the timer
	timer.take_photo(10)

	# Wait for 5 seconds
	time.sleep(5)

	# Stop the timer
	timer.cancel()

	# Wait for 2 seconds
	time.sleep(2)

	# Restart the services
	service_manager.restart()

	# Wait for 1 second
	time.sleep(1)

	# Start the timer
	timer.take_photo(10)

	# Wait for 4 seconds
	time.sleep(4)

	# Exit the system
	service_manager.exit()


if __name__ == "__main__":
	main()