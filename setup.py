"""
Setup script para RED_HOPFIELD.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Leer requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')

setup(
    name="red-hopfield",
    version="2.0.0",
    description="Red de Hopfield para reconstrucción de patrones de letras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RED_HOPFIELD Team",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'hopfield=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
