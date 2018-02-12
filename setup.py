from setuptools import setup
from setuptools import find_packages

setup(name='automated_dinners',
    version='0.1',
    description='Automate buying ingredients for delicious dinners',
    url='https://github.com/menace102/automated_dinners',
    author='Laura and Franklin',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'flask',
        # 'sqlite3',
        'selenium',
        'flask-WTF'
        ],
    zip_safe=False
    )