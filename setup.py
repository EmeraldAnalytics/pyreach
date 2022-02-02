#!/usr/bin/env python

from setuptools import setup

# with open('README.md') as f:
#     long_description = f.read()

setup(
    name="pyreach",
    version="0.1.0",
    description="Python wrapper for Reach API",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    author="mdunndata",
    url="https://github.com/EmeraldAnalytics/pyreach",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    py_modules=["pyreach"],
    install_requires=[
        "requests",
        "tenacity",
    ],
    packages=["pyreach"],
)
