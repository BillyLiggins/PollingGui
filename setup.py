#!/usr/bin/python
""" Setup the setup """
from setuptools import setup

LONG_DESCRIPTION = """
pollingGui
------------
GUI for displaying pooled base currents and CMOS rate in SNO+
"""

setup(
    name="polling-gui",
    version="0.8",
    author="Billy Liggins",
    author_email="billy.liggins@qmul.ac.uk",
    url="https://github.com/BillyLiggins/PollingGui",
    description="SNO+ polling GUI",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    platforms=["any"],
    packages=['pollinggui'],
    package_data={'': ['*.md']},
    install_requires=['pyttk>=0.3.1', 'psycopg2>=2.0.14'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'polling-gui=pollinggui:App',
        ]
    }
)
