from setuptools import setup, find_packages

setup(name='cyberwatch_api',
      version='0.2.0',
      description='Python Api client for the Cyberwatch software',
      long_description=open('README.md').read().strip(),
      long_description_content_type="text/markdown",
      author='CyberWatch SAS',
      packages=find_packages(),
      py_modules=['cyberwatch_api'],
      license='MIT',
      install_requires=['requests>=2.20.1']
      )
