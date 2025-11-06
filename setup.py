from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agentcli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="智能项目初始化助手 - 通过 AI 对话快速创建项目脚手架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentcli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agentcli=agentcli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "agentcli": [
            "templates/**/*",
            "templates/**/**/*",
        ],
    },
)

