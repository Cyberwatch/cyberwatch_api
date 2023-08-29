from setuptools import setup, find_packages

setup(name='cyberwatch_api',
      version='0.3.5',
      description='Python Api client for the Cyberwatch software',
      long_description=open('README.md').read().strip(),
      long_description_content_type="text/markdown",
      author='CyberWatch SAS',
      py_modules=['cyberwatch_api'],
      packages=find_packages(include=['cli.*']),
      license='MIT',
      install_requires=['requests>=2.20.1'],
      scripts=['cli/cyberwatch-cli']
      )
