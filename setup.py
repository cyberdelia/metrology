# -*- coding: utf-8 -*-
from setuptools import setup


with open('LICENSE') as f:
    license = f.read()

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)
