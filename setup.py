"""
Simple package setup script, built to handle finding CTA package.

Author: Ryan Fogle
"""

from setuptools import setup, find_packages
setup(
    name="CTA",
    version="0.2.alpha",
    packages=['cta'],
    python_requires=">=3.10, <4",
)