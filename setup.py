from setuptools import find_packages, setup

setup(
    name='python-freshdesk',
    version='0.9.3',
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='An API for the Freshdesk helpdesk',
    url='https://github.com/sjkingo/python-freshdesk',
    install_requires=['requests', 'python-dateutil'],
    packages=find_packages(),
)
