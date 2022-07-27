import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dl_mqtt_clients",
    version="1.0",
    author="Austin Collins",
    author_email="acollins@technicacorp.com",
    description="Package for clients operating off streamed data via the MQTT Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=['paho-mqtt>=1.3.1',
                      'numpy >= 1.14.5',
                      'tensorflow == 2.2.0+nv20.6',
                      'h5py >= 2.10.0',
                      'scikit-learn >= 0.20.3',
                      'jsonpickle == 0.9.6'],
)
