import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
    name="wireui-TheTimmoth",
    version="0.1.0a2",
    author="Tim Schlottmann",
    author_email="tschlottmann@gmail.com",
    description="A tool for creating and managing wireguard configs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheTimmoth/wireui",
    packages=setuptools.find_packages(),
    keywords=["wireguard"],
    license_file="./LICENSE",
    platforms="Linux",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha", "Environment :: Console"
    ],
    python_requires='>=3.6',
)
