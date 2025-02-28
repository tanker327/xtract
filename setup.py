"""
Setup configuration for the xtract package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xtract",
    version="0.1.0",
    author="Eric Wu",
    author_email="your.email@example.com",
    description="A library for extracting data from X (formerly Twitter) posts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xtract",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.7",
        "certifi>=2023.7.22",
        "charset-normalizer>=3.3.2",
        "idna>=3.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.1",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "xtract=xtract.cli:main",
        ],
    },
)
