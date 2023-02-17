from setuptools import setup

setup(name='cyberwatch_api',
      version='0.1.0',
      description='Python Api client for the Cyberwatch software',
      author='CyberWatch SAS',
      packages=['cyberwatch_api'],
      py_modules=['cyberwatch_api'],
      install_requires=['requests>=2.20.1']
      )
