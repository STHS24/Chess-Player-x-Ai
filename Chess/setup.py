#!/usr/bin/env python3
"""
Setup script for the Chess AI application.
"""

from setuptools import setup, find_packages

setup(
    name="chess_ai",
    version="1.0.0",
    description="A chess application with AI opponent",
    author="Chess AI Project",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "pygame==2.5.2",
        "python-chess==1.9.4",
    ],
    entry_points={
        "console_scripts": [
            "chess-gui=chess_ai.gui.main_app:main",
            "chess-cli=chess_ai.cli.text_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    python_requires=">=3.7",
)
