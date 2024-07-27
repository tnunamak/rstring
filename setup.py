from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rstring",
    version="0.2.0",
    author="Tim Nunamaker",
    author_email="tim.nunamaker@gmail.com",
    description="A tool to stringify code using rsync and manage presets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tnunamak/rstring",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "rstring=rstring.cli:main",
        ],
    },
    install_requires=[
        "pyyaml>=6.0.1",
    ],
    extras_require={
        'dev': ['pytest>=8.3.2'],
    },
)
