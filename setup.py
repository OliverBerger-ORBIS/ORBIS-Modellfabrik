#!/usr/bin/env python3
"""
ORBIS Modellfabrik - Setup Configuration
Echtes Python Packaging für OMF2
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="orbis-modellfabrik",
    version="3.2.0",
    author="ORBIS Team",
    description="ORBIS Modellfabrik Dashboard und Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["omf2*", "session_manager*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "pre-commit>=3.2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "omf2=omf2.omf:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    include_package_data=True,
    package_data={
        "omf2": [
            "config/*.yml",
            "config/*.json",
            "registry/**/*.yml",
            "registry/**/*.json",
            "assets/**/*.svg",
            "assets/**/*.html",
        ],
    },
)
