"""
Setup script for Abhikarta LLM Abstraction System

© 2025-2030 All rights reserved Ashutosh Sinha
email: ajsinha@gmail.com
https://www.github.com/ajsinha/abhikarta
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Get version from __init__.py
version = '2.0.0'

setup(
    name='abhikarta-llm',
    version=version,
    description='Unified LLM abstraction system with multi-provider support',
    long_description=read_file('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Ashutosh Sinha',
    author_email='ajsinha@gmail.com',
    url='https://github.com/ajsinha/abhikarta',
    license='Proprietary',
    
    packages=find_packages(),
    include_package_data=True,
    
    # Core dependencies
    install_requires=[
        'pydantic>=2.0',
    ],
    
    # Optional provider dependencies
    extras_require={
        'anthropic': ['anthropic>=0.18.0'],
        'openai': ['openai>=1.0.0'],
        'google': ['google-generativeai>=0.3.0'],
        'meta': ['replicate>=0.15.0'],
        'huggingface': ['transformers>=4.30.0'],
        'aws': ['boto3>=1.28.0'],
        'all': [
            'anthropic>=0.18.0',
            'openai>=1.0.0',
            'google-generativeai>=0.3.0',
            'replicate>=0.15.0',
            'transformers>=4.30.0',
            'boto3>=1.28.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    # Keywords
    keywords='llm ai abstraction anthropic openai google meta huggingface aws bedrock',
    
    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/ajsinha/abhikarta/wiki',
        'Source': 'https://github.com/ajsinha/abhikarta',
        'Tracker': 'https://github.com/ajsinha/abhikarta/issues',
    },
)
