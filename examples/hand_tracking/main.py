import logging
from eymos import ServiceManager, log
from eymos.services import CameraService, WindowService
from services.hand_tracking import HandTrackingService


def main():

	# Initialize the service manager
	manager = ServiceManager()
	manager.set_config({
		"window": {
			"resizable": True
		}
	})

	# Add the services to the manager
	camera = manager.add("camera", CameraService)
	window = manager.add("window", WindowService)
	hand_tracking = manager.add("hand_tracking", HandTrackingService)

	# Start the services
	manager.start()

	# Start the window main loop
	window.mainloop()


if __name__ == "__main__":
	main()
