from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "LICENSE"), "r", encoding="utf-8") as fh:
    license_text = fh.read()

setup(
    name="eymos",
    version="1.1.0",
    author="EymoLabs",
    author_email="info@dzin.es",
    description="EymOS - Lightweight Middleware for Robotics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EymoLabs/eymos",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python>=4.5.3.56",
        "Pillow>=8.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering"
    ],
    python_requires='>=3.6',
    license="Custom License",
    keywords="robotics middleware eymos lightweight",
    project_urls={
        "Bug Reports": "https://github.com/EymoLabs/eymos/issues",
        "Source": "https://github.com/EymoLabs/eymos"
    },
)
