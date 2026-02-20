#!/usr/bin/env python3
"""
ORBIS Modellfabrik - Setup Configuration
Python Packaging für Session Manager und Projekt-Tools

Version wird aus package.json gelesen (Single Source of Truth für OSF + Session Manager).
"""

import json
from pathlib import Path

from setuptools import find_packages, setup

# Version aus package.json (Single Source of Truth)
package_json_path = Path(__file__).parent / "package.json"
version = "0.0.0"
if package_json_path.exists():
    with open(package_json_path, encoding="utf-8") as f:
        version = json.load(f).get("version", version)

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
    name="orbis-smartfactory",
    version=version,
    author="ORBIS Team",
    description="ORBIS SmartFactory – Session Manager für Replay-Environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["session_manager*"]),
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
)
