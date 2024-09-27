<p align="center">
  <a href="https://github.com/EymoLabs/eymos">
    <img src="./logo.png" alt="EymOS banner" width="258" height="100">
  </a>
  <h3 align="center">EymOS - Lightweight Middleware for Robotics</h3>
  <p align="center">
    EymOS is a lightweight and efficient middleware for robotics, providing streamlined node communication and device control, designed for simplicity and high performance
    <br>
    <a href="https://github.com/EymoLabs/eymos/issues/new?template=bug.md">Report bug</a>
    ·
    <a href="https://github.com/EymoLabs/eymos/issues/new?template=feature.md&labels=feature">Request feature</a>
  </p>
</p>


## Table of contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
	- [Prerequisites](#prerequisites)
	- [Setup](#setup)
- [Usage](#usage)
- [Services](#services)
	- [First steps](#first-steps)
    - [Dependencies](#dependencies)
    - [Methods](#methods)
    - [Attributes](#attributes)
    - [Definitions](#definitions)
- [What's included](#whats-included)
- [Bugs and feature requests](#bugs-and-feature-requests)
- [Creators](#creators)
- [Collaborators](#collaborators)
- [License](#license)


## Introduction

EymOS is a lightweight and efficient middleware designed for robotics applications, inspired by the flexibility and modularity of systems like ROS, but optimized to be faster and lighter.

Originally developed for the robot Eymo, EymOS has evolved into an independent platform that provides all the essential functionalities for node communication, device control, and process management, with a focus on simplicity and performance.

## Features

* Lightweight and fast communication between nodes
* Device control and process management for small-scale robots
* Minimal resource usage, ideal for embedded systems and small robots
* Easy integration with cloud services for advanced features

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.12 or higher

### Setup with pip
Use `pip` to install the package from PyPI.

1. Install the package using `pip`:
   ```sh
   pip install eymos
   ```
2. Import the package and [start using it](#usage).

### Setup from source
Alternatively, you can clone the repository and install the package from the source code.

1. Clone the repository:
   ```sh
   git clone https://github.com/EymoLabs/eymos.git
   ```
2. Navigate to the project directory and install the required dependencies:
   ```sh
   cd eymos
   pip install -r requirements.txt
   ```
3. You’re ready to use EymOS! [Start using it](#usage).

## Usage
After installing the package, you need to create the services for your robot, which will handle the communication between nodes and devices. Next, you could initialize them and start the service.

### Create a new service
Create a new Python file for your service, and define the class for the service. The service should inherit from the `Service` class provided by EymOS.
```python
from eymos import Service, utils, log

class TimerService(Service):
	def init(self):
		"""Initialize the service. Required."""
		self.__time = 0
		self.__is_running = False
		self.__max_time = self._config.get("max_time", 300)
		self._loop_delay = 1  # Control the loop delay in seconds

	def destroy(self):
		"""Destroy the service. Required."""
		self.__time = None
		self.__is_running = None
		self.__max_time = None

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread) Optional."""
		# Not required for this service
		pass

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
```

### Initialize and start the service
Create a new Python file for your main program, and initialize the service manager. Add the services to the manager, and start the services.
```python
from eymos import ServiceManager
from eymos.services import CameraService
from services.timer import TimerService

def main():
	# Create a new service manager
	service_manager = ServiceManager()
	
	# Link a configuration to the service manager
	service_manager.set_config_file("config.json")
	
	# Add the services to the manager
	service_manager.add("timer", TimerService)
	service_manager.add("camera", CameraService)
	
	# Initialize the services
	service_manager.start()	# Start the first service added, and then the rest

if __name__ == "__main__":
	main()
```

### Configuration file
Create a configuration file for the services, and specify the parameters for each service.
```json
{
	"timer": {
		"max_time": 300
	},
	"camera": {
		"resolution": [640, 480],
		"fps": 30
	}
}
```

Optionally, you could use the `set_config` method to set the configuration dictionary directly, instead of using a configuration file.

```python
service_manager.set_config({
	"timer": {
		"max_time": 300
	},
})
```

## Services
EymOS provides a set of services that can be used to control devices and processes in your robot. Each service is defined as a class that inherits from the `Service` class, and implements the required methods and attributes.

### First steps
When a service is initialized, some actions are performed automatically, to ensure the service is correctly set up and ready to run.

**On start**, when a service is started, the `init` method is called, which initializes the variables and configurations for the service. This method is required for all services. Additionally, a new asyncronous thread is created for the service, which will run the `before` and `loop` methods in a loop, with a delay specified by the `loop_delay` attribute.

**On stop**, when a service is stopped, the `destroy` method is called, which cleans up the resources used by the service. This method is required for all services.

### Dependencies
A service can define dependencies on other services, which will be started before the service is started. This is useful when a service requires another service to be running before it can start.

To define dependencies, set the [`DEPENDENCIES`](#definitions) constant in the service class, with the names of the services that the service depends on.

```python
class MyService(Service):
	DEPENDENCIES = ["camera", "motor"]
```

### Methods
A service can define custom methods to perform specific actions or operations. These methods can be created as needed, and can be called from other services or external programs.

| Method | Description | Required |
| --- | --- | --- |
| `init` | Initialize the service, setting up the variables and configurations. | Yes |
| `destroy` | Destroy the service, cleaning up the resources used by the service. | Yes |
| `before` | Perform actions before the loop starts. This method is called in the service thread, before the loop method. | No |
| `loop` | Perform the main actions of the service. This method is called in the service thread, in a loop with a delay specified by the `loop_delay` attribute or the `LOOP_DELAY` constant. | No |

Additionally, a service has some reserved methods that should not be overridden:

| Method | Description |
| --- | --- |
| `start` | Start the service, initializing the service and starting the service thread. When the service is started, automatically starts all the other services that have not been started yet. If the service has dependencies, starts the dependencies first. |
| `stop` | Stop the service, stopping the service thread and cleaning up the resources used by the service. When the service is stopped, automatically stops all the other services that depend on this service. |
| `is_initialized` | Check if the service has been initialized. |
| `__init__` | Initialize the service instance, setting up the service attributes. |
| `__reboot` | Reboot all the services, stopping and starting all the services. |
| `__thread__execution` | Execute the service thread, calling the `before` and `loop` methods in a loop with the specified delay. |
| `__start_other_service` | Start another service that has not been started yet. |

### Attributes
The service class has some attributes that can be used to configure the service during the execution, or to access some information.

| Attribute | Description                                                                                                                                                                      | Default |
| --- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| --- |
| _config | The configuration dictionary for the service. It contains the parameters specified in the configuration file (only the configuration dictionary identified by the service name). | `{}` (set in constructor) |
| _global_config | The global configuration dictionary for all the services. It contains the parameters specified in the global configuration file.                                                 | `None` (set in constructor) |
| _loop_delay | The delay between each loop iteration, in seconds. It controls the frequency of the loop method.                                                                                 | `self.LOOP_DELAY` |
| _name | The name of the service. It allows, for example, identifying other services and accessing to them (e.g., `self._services["camera"].get_frame()`).                                | `None` (set in constructor) |
| _services | The dictionary of all the services in the service manager. It allows accessing other services and calling their methods.                                                         | `None` |
| __errors | The number of consecutive errors that have occurred during the execution of the service.                                                                                         | `0` |
| __initialized | A flag that indicates if the service has been initialized.                                                                                                                       | `False` |
| __init_try | The number of times the service has tried to initialize.                                                                                                                         | `0` |
| __thread | The thread object that is running in the service.                                                                                                                                | `None` |


### Definitions
Some constants are defined in the service class, which can be used to configure the service or to define some properties.

| Constant | Description                                                                                                                          | Default |
| --- |--------------------------------------------------------------------------------------------------------------------------------------| --- |
| DEPENDENCIES | The list of services that the service depends on. The services in the list will be started before the service is started.            | `[]`
| ERROR_INTERVAL | The interval between each error, in seconds. It controls the frequency of the error messages and helps to avoid flooding the logs.    | `5` |
| LOOP_DELAY | The default delay between each loop iteration, in seconds. It controls the frequency of the loop method.                             | `0.25` (4 times per second) |
| MAX_ERRORS | The maximum number of consecutive errors that can occur before the service is stopped. Can be disabled by setting it to `-1`.        | `5` |
| MAX_ERRORS_REBOOT | The maximum number of consecutive errors that can occur before **all the services** are rebooted. Can be disabled by setting it to `-1`. | `-1` (disabled) |


## What's included

Within the download you'll find the following directories and files:

```text
eymos/
├── services/
│   ├── __init__.py
│   └── camera.py
├── __init__.py
├── log.py
├── service.py
├── service_manager.py
└── utils.py
```

## Bugs and feature requests
Have a bug or a feature request? Please search for existing and closed issues. If your problem or idea is not addressed yet, [open a new issue](https://github.com/EymoLabs/eymos/issues/new).

## Creators
This project was developed entirely by Xavi Burgos, as part of the [EymoLabs](https://github.com/EymoLabs) team.

### Xavi Burgos
- Website: [xburgos.es](https://xburgos.es)
- LinkedIn: [@xavi-burgos](https://www.linkedin.com/in/xavi-burgos/)
- GitHub: [@xavi-burgos99](https://github.com/xavi-burgos99)
- X (Twitter): [@xavi_burgos14](https://x.com/xavi_burgos14)

## Collaborators
Special thanks to the following people from the [EymoLabs](https://github.com/EymoLabs) team for their contributions to the project:

### Yeray Cordero
- GitHub: [@yeray142](https://github.com/yeray142/)
- LinkedIn: [@yeray142](https://linkedin.com/in/yeray142/)

### Javier Esmorris
- GitHub: [@jaesmoris](https://github.com/jaesmoris/)
- LinkedIn: [Javier Esmoris Cerezuela](https://www.linkedin.com/in/javier-esmoris-cerezuela-50840b253/)

### Gabriel Juan
- GitHub: [@GabrielJuan349](https://github.com/GabrielJuan349/)
- LinkedIn: [@gabi-juan](https://linkedin.com/in/gabi-juan/)

### Samya Karzazi
- GitHub: [@SamyaKarzaziElBachiri](https://github.com/SamyaKarzaziElBachiri)
- LinkedIn: [Samya Karzazi](https://linkedin.com/in/samya-k-2ba678235/)

## License
This project is licensed under a custom license, that allows you to **use and modify the code** for any purpose, as long as you **provide attribution to the original authors**, but you **cannot distribute the code** or any derivative work **without permission**. For more information, see the [LICENSE](LICENSE) file.
