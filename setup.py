# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='metrology',
    version='0.3.2',
    description='A library to easily measure what\'s going on in your python.',
    author='Timothée Peignier',
    author_email='timothee.peignier@tryphon.org',
    url='https://github.com/cyberdelia/metrology',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'atomic>=0.3.2',
        'bintrees>=1.0.0'
    ],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
