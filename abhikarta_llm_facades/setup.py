"""
Setup configuration for Abhikarta LLM Facades

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="abhikarta-llm-facades",
    version="1.0.0",
    author="Ashutosh Sinha",
    author_email="ajsinha@gmail.com",
    description="Unified, provider-agnostic interface for Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajsinha/abhikarta-llm-facades",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "google-generativeai>=0.3.0",
            "cohere>=4.0.0",
            "mistralai>=0.0.11",
            "groq>=0.4.0",
            "boto3>=1.28.0",
            "huggingface_hub>=0.19.0",
            "transformers>=4.35.0",
            "torch>=2.0.0",
            "together>=1.0.0",
            "replicate>=0.20.0",
            "tiktoken>=0.5.0",
            "pillow>=10.0.0",
            "accelerate>=0.24.0",
            "bitsandbytes>=0.41.0",
            "sentence-transformers>=2.2.0"
        ],
        "openai": ["openai>=1.0.0", "tiktoken>=0.5.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "google": ["google-generativeai>=0.3.0"],
        "cohere": ["cohere>=4.0.0"],
        "mistral": ["mistralai>=0.0.11"],
        "groq": ["groq>=0.4.0"],
        "aws": ["boto3>=1.28.0"],
        "huggingface": ["huggingface_hub>=0.19.0", "transformers>=4.35.0", "torch>=2.0.0"],
        "together": ["together>=1.0.0"],
        "replicate": ["replicate>=0.20.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0"
        ]
    },
    include_package_data=True,
    package_data={
        "facades": ["*.json"],
    },
    entry_points={
        "console_scripts": [
            "abhikarta-llm=facades.cli:main",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/ajsinha/abhikarta-llm-facades/docs",
        "Source": "https://github.com/ajsinha/abhikarta-llm-facades",
        "Bug Reports": "https://github.com/ajsinha/abhikarta-llm-facades/issues",
    },
    keywords="llm ai ml nlp language-models openai anthropic google facade",
    zip_safe=False,
)
