#!/usr/bin/python3

# -*- coding: utf-8 -
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='simplePipes',
    version='1.0',
    description='Python package to solve simple pipe systems',
    long_description=readme,
    author='Alejandro Morales',
    author_email='lmoralesm@unal.edu.co',
    url='https://github.com/lamhydro/simplePipes',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

