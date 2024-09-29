import io
import cv2
import base64
import logging
import numpy as np
from PIL import Image
from pynput import keyboard
from eymos import Service, log


class DependencyLoader:
	TKINTER = False

	@staticmethod
	def is_tkinter():
		"""Check if tkinter is installed."""
		return DependencyLoader.TKINTER


try:
	import tkinter as tk
	from tkinter import Canvas
	from PIL import ImageTk
	DependencyLoader.TKINTER = True
except ImportError:
	pass


class ImageSize:
	COVER = 0
	CONTAIN = 1
	STRETCH = 2


class WindowService(Service):
	DEFAULT_FPS = 60
	DEFAULT_RESOLUTION = [480, 270]
	APP_LOGO = "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"

	def __init__(self, name: str, config: dict, services: dict):
		"""Initialize the service.
		Args:
			name (str): The name of the service.
			config (dict): The system configuration.
			services (dict, optional): The services to use. Defaults to {}.
		"""
		# Initialize the service attributes
		self.__fps = None
		self.__title = None
		self.__resizable = None
		self.__always_on_top = None
		self.__background = None
		self.__border = None
		self.__width = None
		self.__height = None
		self.__draggable = None
		self.__toggle_visibility = None
		self.__frame = None
		self.__tk_root = None
		self.__tk_icon = None
		self.__tk_image = None
		self.__tk_photo = None
		self.__tk_canvas = None
		self.__tk_canvas_img = None
		self.__tk_is_visible = None

		# Call the parent class constructor
		super().__init__(name, config, services)

	def init(self):
		"""Initialize the service."""
		self.__fps = self._config.get('fps', self.DEFAULT_FPS)
		self._loop_delay = 1 / self.__fps
		self.__title = self._config.get('title', 'EymOS')
		self.__resizable = self._config.get('resizable', False)
		self.__always_on_top = self._config.get('always_on_top', True)
		self.__background = self._config.get('background', 'black')
		self.__border = self._config.get('border', False)
		self.__width = self._config.get('width', self.DEFAULT_RESOLUTION[0])
		self.__height = self._config.get('height', self.DEFAULT_RESOLUTION[1])
		self.__draggable = self._config.get('draggable', True)
		self.__toggle_visibility = self._config.get('toggle_visibility', {'key': 'h', 'modifiers': ['ctrl']})
		self.__frame = 0
		self.__tk_root = None
		self.__tk_icon = self.APP_LOGO
		self.__tk_image = None
		self.__tk_photo = None
		self.__tk_canvas = None
		self.__tk_canvas_img = None
		self.__tk_is_visible = True

		# Initialize the tkinter window
		self.__tk_init()

	def destroy(self):
		"""Destroy the service."""
		self.__fps = None
		self.__title = None
		self.__resizable = None
		self.__always_on_top = None
		self.__background = None
		self.__border = None
		self.__width = None
		self.__height = None
		self.__draggable = None
		self.__toggle_visibility = None
		self.__frame = None
		self.__tk_icon = None
		self.__tk_image = None
		self.__tk_photo = None
		self.__tk_canvas = None
		self.__tk_canvas_img = None
		self.__tk_is_visible = None

		# Destroy the tkinter window from manager
		if self._manager:
			self._manager.on_stop(self.__tk_root.quit)

	def loop(self):
		"""Service loop."""
		if not DependencyLoader.is_tkinter():
			return

		# Update the tkinter window
		if self.__tk_root is not None:
			self.__tk_update()

	def mainloop(self):
		"""Start the tkinter main loop."""
		# Check if tkinter is installed
		if self.__tk_root is None:
			return

		# Start the tkinter main loop
		self.__tk_root.mainloop()

	def draw(self, image: np.ndarray, size: int = ImageSize.COVER):
		"""Draw the image on the window.
		Args:
			image (np.ndarray): The image to draw.
		"""
		# Draw the image on the tkinter canvas
		self.__tk_draw(image, size)

	def __tk_init(self):
		"""Initializes tkinter for PCs to emulate the screen."""
		# Check if tkinter is installed
		if not DependencyLoader.is_tkinter():
			log('Tkinter is not installed. The window service is disabled.', logging.WARNING)
			return

		# Create the tkinter window
		geometry = f'{self.__width}x{self.__height}'
		self.__tk_root = tk.Tk()
		self.__tk_root.title(self.__title)
		self.__tk_root.geometry(geometry)
		self.__tk_root.resizable(self.__resizable, self.__resizable)

		# Set the window always on top
		if self.__always_on_top:
			self.__tk_root.lift()

		# Remove the window border
		if not self.__border:
			self.__tk_root.overrideredirect(True)
			self.__tk_root.config(bg=self.__background)

		# Create the tkinter canvas
		self.__tk_image = Image.new('RGB', (self.__width, self.__height), 'black')
		self.__tk_photo = ImageTk.PhotoImage(self.__tk_image)
		self.__tk_canvas = Canvas(self.__tk_root, width=self.__width, height=self.__height, bg=self.__background, highlightthickness=0)
		self.__tk_canvas_img = self.__tk_canvas.create_image(0, 0, anchor='nw', image=self.__tk_photo)
		self.__tk_canvas.pack()

		# Set the window icon
		if self.__tk_icon:
			icon_data = base64.b64decode(self.__tk_icon)
			icon_image = Image.open(io.BytesIO(icon_data))
			self.__tk_icon = ImageTk.PhotoImage(icon_image)
			self.__tk_root.iconphoto(False, self.__tk_icon)

		# Enable dragging
		if self.__draggable:
			self.__tk_drag(self.__tk_root)

		# Enable visibility toggle
		if self.__toggle_visibility:
			self.__tk_visibility(self.__tk_root)

	def __tk_drag(self, root):
		"""Enable dragging for the tkinter window.
		Args:
			root (tk.Tk): The tkinter window.
		"""
		# Check if tkinter is installed
		if not DependencyLoader.is_tkinter():
			return

		# Initialize the start coordinates
		coords = {"x": 0, "y": 0}

		# Function to start dragging
		def start_drag(event, coords):
			coords["x"] = event.x
			coords["y"] = event.y

		# Function to stop dragging
		def stop_drag(event, coords):
			coords["x"] = None
			coords["y"] = None

		# Function to drag the window
		def drag(event, coords):
			x = root.winfo_x() + event.x - coords["x"]
			y = root.winfo_y() + event.y - coords["y"]
			root.geometry(f'+{x}+{y}')

		# Remove the window border
		if not self.__border:
			self.__tk_root.overrideredirect(True)

		# Bind the mouse events
		root.bind('<ButtonPress-1>', lambda event: start_drag(event, coords))
		root.bind('<ButtonRelease-1>', lambda event: stop_drag(event, coords))
		root.bind('<B1-Motion>', lambda event: drag(event, coords))

	def __tk_visibility(self, root):
		"""Enable visibility toggle for the tkinter window.
		Args:
			root (tk.Tk): The tkinter window.
		"""
		# Check if tkinter is installed
		if not DependencyLoader.is_tkinter():
			return

		# Check if the toggle key is set
		if not self.__toggle_visibility:
			return

		# Initialize the modifier keys
		modifiers = self.__toggle_visibility.get('modifiers', [])
		key_char = self.__toggle_visibility.get('key', 'h')

		# Initialize the pressed keys
		keys = {"ctrl": False, "shift": False, "alt": False, "meta": False}

		# Function to check pressed keys
		def on_press(key, keys):
			if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
				keys["ctrl"] = True
			elif keyboard.Key.shift_l == key or keyboard.Key.shift_r == key:
				keys["shift"] = True
			elif keyboard.Key.alt_l == key or keyboard.Key.alt_r == key:
				keys["alt"] = True
			elif keyboard.Key.cmd_l == key or keyboard.Key.cmd_r == key:
				keys["meta"] = True
			is_pressed = True
			for modifier in modifiers:
				if not keys[modifier]:
					is_pressed = False
					break
			if type(key) != keyboard.KeyCode:
				return
			if is_pressed and key_char == key.char:
				self.__tk_is_visible = not self.__tk_is_visible
				if self.__tk_is_visible:
					log('The window is visible')
					root.deiconify()
				else:
					log('The window is hidden')
					root.withdraw()

		# Function to check released keys
		def on_release(key, keys):
			if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
				keys["ctrl"] = False
			elif keyboard.Key.shift_l == key or keyboard.Key.shift_r == key:
				keys["shift"] = False
			elif keyboard.Key.alt_l == key or keyboard.Key.alt_r == key:
				keys["alt"] = False
			elif keyboard.Key.cmd_l == key or keyboard.Key.cmd_r == key:
				keys["meta"] = False

		# Start the listener
		listener = keyboard.Listener(on_press=lambda key: on_press(key, keys), on_release=lambda key: on_release(key, keys))
		listener.start()

	def __tk_update(self):
		"""Update the tkinter window."""
		# Check if the window is visible or the canvas is not set
		if not self.__tk_is_visible or self.__tk_canvas is None:
			return

		# Update the frame
		self.__frame += 1

		# Update width and height
		width = self.__tk_root.winfo_width()
		height = self.__tk_root.winfo_height()
		if width != self.__width:
			self.__width = width
		if height != self.__height:
			self.__height = height

		# Set the always on top
		if self.__always_on_top:
			self.__tk_root.attributes('-topmost', True)

		# Draw the image
		self.__tk_draw()

		# Update the window
		self.__tk_root.update_idletasks()
		self.__tk_root.update()

	def __tk_clear(self):
		"""Clear the tkinter canvas."""
		# Draw a black image
		self.__tk_image = Image.new('RGB', (self.__width, self.__height), 'black')

		# Convert the image to tkinter
		self.__tk_photo = ImageTk.PhotoImage(self.__tk_image)

		# Update the canvas
		self.__tk_canvas.itemconfig(self.__tk_canvas_img, image=self.__tk_photo)

	def __tk_draw(self, image: np.ndarray = None, size: int = ImageSize.COVER):
		"""Draw the image on the tkinter canvas.
		Args:
			image (Image, optional): The image to draw. Defaults to None.
		"""
		# Check if the image is set
		if image is None:
			return

		# Resize the image
		if size == ImageSize.COVER:
			image = self.__image_resize_cover(image, self.__width, self.__height)
		elif size == ImageSize.CONTAIN:
			image = self.__image_resize_contain(image, self.__width, self.__height)
		elif size == ImageSize.STRETCH:
			image = self.__image_resize_stretch(image, self.__width, self.__height)

		# Convert the image to PIL
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = Image.fromarray(image)

		# Convert the image to tkinter
		self.__tk_photo = ImageTk.PhotoImage(image)

		# Update the canvas
		self.__tk_canvas.itemconfig(self.__tk_canvas_img, image=self.__tk_photo)

	@staticmethod
	def __image_resize_cover(image: np.ndarray, width: int, height: int) -> np.ndarray:
		"""Resize the image to cover the window.
		Args:
			image (np.ndarray): The image to resize.
			width (int): The width of the window.
			height (int): The height of the window.
		Returns:
			np.ndarray: The resized image.
		"""
		# Get the image size
		image_width, image_height = image.shape[1], image.shape[0]

		# Calculate the resize ratio
		ratio = max(width / image_width, height / image_height)

		# Resize the image
		image = cv2.resize(image, (int(image_width * ratio), int(image_height * ratio)))

		# Calculate the cropping
		crop_x = (image.shape[1] - width) // 2
		crop_y = (image.shape[0] - height) // 2

		# Crop the image
		image = image[crop_y:crop_y + height, crop_x:crop_x + width]

		# Return the image
		return image

	@staticmethod
	def __image_resize_contain(image: np.ndarray, width: int, height: int) -> np.ndarray:
		"""Resize the image to contain the window.
		Args:
			image (np.ndarray): The image to resize.
			width (int): The width of the window.
			height (int): The height of the window.
		Returns:
			np.ndarray: The resized image.
		"""
		# Get the image size
		image_width, image_height = image.shape[1], image.shape[0]

		# Calculate the resize ratio
		ratio = min(width / image_width, height / image_height)

		# Resize the image
		image = cv2.resize(image, (int(image_width * ratio), int(image_height * ratio)))

		# Calculate the padding
		padding = (height - image.shape[0]) // 2

		# Add the padding
		image = cv2.copyMakeBorder(image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])

		# Return the image
		return image

	@staticmethod
	def __image_resize_stretch(image: np.ndarray, width: int, height: int) -> np.ndarray:
		"""Resize the image to stretch the window.
		Args:
			image (np.ndarray): The image to resize.
			width (int): The width of the window.
			height (int): The height of the window.
		Returns:
			np.ndarray: The resized image.
		"""
		# Resize the image
		image = cv2.resize(image, (width, height))

		# Return the image
		return image
