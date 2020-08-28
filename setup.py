import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twinpy",
    version="3.0.1",
    author="Mehmet Helvacıköylü",
    author_email="mhelvacikoylu@gmail.com",
    description="Python client for Twino MQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twino-framework/twinpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
