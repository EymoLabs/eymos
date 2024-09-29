import cv2
import base64
from PIL import Image
from eymos.service import Service


class FrameType:
	IMAGE = 0    # PIL Image
	NUMPY = 1    # Numpy array
	LIST = 2     # List
	BYTES = 3    # Bytes
	BASE64 = 4   # Base64 string


class CameraService(Service):
	DEFAULT_FPS = 25
	DEFAULT_RESOLUTION = [640, 480]

	def __init__(self, name: str, config: dict, services: dict):
		"""Initialize the service.
		Args:
			name (str): The name of the service.
			config (dict): The system configuration.
			services (dict, optional): The services to use. Defaults to {}.
		"""
		# Initialize the service attributes
		self.__camera = None
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None
		self.__last_frame_base64 = None
		self.__rotate_frame = None
		self.__resolution = None
		self.__fps = None

		# Call the parent class constructor
		super().__init__(name, config, services)

	def init(self):
		"""Initialize the service."""
		self.__camera = None
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None
		self.__last_frame_base64 = None
		self.__rotate_frame = self._config.get('rotate_frame', False)
		self.__resolution = self._config.get('resolution', self.DEFAULT_RESOLUTION)
		self.__fps = self._config.get('fps', self.DEFAULT_FPS)
		self._loop_delay = 1 / self.__fps

	def destroy(self):
		"""Destroy the service."""
		if self.__camera is not None:
			self.__camera.release()
			self.__camera = None
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None
		self.__last_frame_base64 = None
		self.__rotate_frame = None
		self.__resolution = None
		self.__fps = None
		self._loop_delay = self.LOOP_DELAY

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		# Connect to the camera
		self.__camera = cv2.VideoCapture(self._config.get('camera', 0))

		# Check if the camera is opened
		if not self.__camera.isOpened():
			raise RuntimeError("Could not open camera")

	def loop(self):
		"""Service loop."""
		# Reset the last frame. This optimizes the memory usage by reusing the last frame.
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None
		self.__last_frame_base64 = None

	def __convert_frame(self, frame_type: int):
		"""Convert the camera frame.
		Args:
			frame_type (int): The frame type.
		Returns:
			Any: The converted frame, or None if the frame type is invalid.
		"""
		# Get the last frame and check if it exists
		frame = self.__last_frame
		if frame is None:
			return None

		# Do not convert the frame if it is in numpy format
		if frame_type == FrameType.NUMPY:
			return frame

		# Convert the frame to a list, if needed
		if frame_type == FrameType.LIST:
			if self.__last_frame_list is None:
				self.__last_frame_list = frame.tolist()
			return self.__last_frame_list

		# Convert the frame to bytes, if needed
		if frame_type == FrameType.BYTES:
			if self.__last_frame_bytes is None:
				self.__last_frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
			return self.__last_frame_bytes

		# Convert the frame to a PIL image, if needed
		if frame_type == FrameType.IMAGE:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			if self.__last_frame_image is None:
				self.__last_frame_image = Image.fromarray(frame)
			return self.__last_frame_image

		# Convert the frame to a base64 string, if needed
		if frame_type == FrameType.BASE64:
			if self.__last_frame_base64 is None:
				retval, buffer = cv2.imencode('.png', frame)
				self.__last_frame_base64 = base64.b64encode(buffer).decode('utf-8')
			return self.__last_frame_base64

		# Return None if the frame type is invalid
		return None

	def get_frame(self, frame_type: int = FrameType.NUMPY):
		"""Get the camera frame.
		Args:
			frame_type (int, optional): The frame type. Defaults to FrameType.NUMPY.
		Returns:
			Any: The camera frame, or None if the frame type is invalid.
		"""
		# Get the last frame
		frame = self.__last_frame

		# Return the converted frame if it exists
		if frame is not None:
			return self.__convert_frame(frame_type)

		# Return None if the camera is not connected
		if self.__camera is None:
			return None

		# Read the frame from the camera
		ret, frame = self.__camera.read()

		# Return None if the frame could not be read
		if not ret:
			return None

		# Resize and rotate the frame
		frame = cv2.resize(frame, tuple(self.__resolution))

		# Rotate the frame if needed
		if self.__rotate_frame:
			frame = cv2.rotate(frame, cv2.ROTATE_180)

		# Save the last frame
		self.__last_frame = frame

		# Return the converted frame
		return self.__convert_frame(frame_type)
