from setuptools import setup, find_packages

setup(name='cyberwatch_api',
      version='0.3.3',
      description='Python Api client for the Cyberwatch software',
      long_description=open('README.md').read().strip(),
      long_description_content_type="text/markdown",
      author='CyberWatch SAS',
      packages=find_packages(where='cli'),
      package_dir={"": "cli"},
      py_modules=['cyberwatch_api'],
      license='MIT',
      install_requires=['requests>=2.20.1'],
      scripts=['cli/cyberwatch-cli']
      )
