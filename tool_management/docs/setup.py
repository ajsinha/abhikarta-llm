"""
Abhikarta LLM - Tool Management Framework
Setup Configuration

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha (ajsinha@gmail.com)
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="abhikarta-tool-management",
    version="1.0.0",
    author="Ashutosh Sinha",
    author_email="ajsinha@gmail.com",
    description="A comprehensive tool management framework for Large Language Models",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/ashutoshsinha/abhikarta-tool-management",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.24.0",  # For async HTTP requests
        "pydantic>=2.0.0",  # For data validation
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "mcp": [
            "anthropic>=0.18.0",  # For MCP protocol support
        ],
        "llm": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
        "all": [
            "httpx>=0.24.0",
            "pydantic>=2.0.0",
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "abhikarta-tools=tool_management.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "tool_management": ["py.typed"],
    },
    zip_safe=False,
    keywords=[
        "llm",
        "tools",
        "ai",
        "machine-learning",
        "mcp",
        "model-context-protocol",
        "anthropic",
        "openai",
        "claude",
        "gpt",
        "tool-management",
        "function-calling",
    ],
    project_urls={
        "Documentation": "https://github.com/ashutoshsinha/abhikarta-tool-management/docs",
        "Source": "https://github.com/ashutoshsinha/abhikarta-tool-management",
        "Tracker": "https://github.com/ashutoshsinha/abhikarta-tool-management/issues",
    },
)
