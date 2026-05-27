from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ness-test-project",
    version="0.1.0",
    author="Test Automation Team",
    description="eBay E2E Test Automation using Playwright and Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ranAdler/ness-test-project",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)