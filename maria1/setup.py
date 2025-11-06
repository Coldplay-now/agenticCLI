from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="maria1",
    version="0.1.0",
    author="Developer",
    author_email="developer@example.com",
    description="命令行版超级玛丽游戏",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "maria1=maria1.cli:cli",
        ],
    },
)

