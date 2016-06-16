from setuptools import find_packages, setup

from freshdesk import __version__

setup(
    name='python-freshdesk',
    version=__version__,
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='An API for the Freshdesk helpdesk',
    url='https://github.com/sjkingo/python-freshdesk',
    install_requires=['requests', 'python-dateutil'],
    packages=find_packages(),
)
