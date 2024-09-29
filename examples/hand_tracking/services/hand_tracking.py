import cv2
import mediapipe as mp
from eymos import Service


class HandTrackingService(Service):
	def init(self):
		"""Initialize the service."""
		# Setting up initial attributes
		self._loop_delay = 0.04   # Delay between each loop
		self.__hand_detector = None  # Placeholder for the hand detection model
		self.__model_complexity = self._config.get('model_complexity', 0)  # Simplified hand model for real-time
		self.__min_detection_confidence = self._config.get('min_detection_confidence', 0.5)   # Minimum confidence to detect hands
		self.__min_tracking_confidence = self._config.get('min_tracking_confidence', 0.5)  # Minimum confidence to track hands

	def destroy(self):
		"""Clean up resources before stopping the service."""
		if self.__hand_detector:
			self.__hand_detector.close()  # Clean up MediaPipe hand detector
		self._hand_detector = None
		self._model_complexity = None
		self._min_detection_confidence = None
		self._min_tracking_confidence = None

	def before(self):
		"""Prepare anything that needs to be initialized outside the main thread."""
		self.__hand_detector = mp.solutions.hands.Hands(
			model_complexity=self.__model_complexity,
			min_detection_confidence=self.__min_detection_confidence,
			min_tracking_confidence=self.__min_tracking_confidence
		)

	def loop(self):
		"""Main loop where the hand detection logic will run."""
		# Get the CameraService from the service manager
		camera_service = self._services.get('camera')
		if camera_service is None:
			return

		# Get the latest frame from CameraService
		frame = camera_service.get_frame()
		if frame is None:
			return

		# Convert the frame from BGR to RGB as required by MediaPipe
		image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# Process the frame to detect hands
		results = self.__hand_detector.process(image_rgb)

		# If hands are detected, draw landmarks on the frame
		if results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				mp.solutions.drawing_utils.draw_landmarks(
					frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
				)

		# Display the processed frame in WindowService
		window_service = self._services.get('window')
		if window_service:
			window_service.draw(frame)
