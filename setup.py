from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="verdictos-scan",
    version="1.0.0",
    author="VerdictOS",
    author_email="admin@verdictos.tech",
    description="Security scanner for AI-generated code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/verdictos/scan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "verdictos-scan=verdictos_scan:main",
        ],
    },
    py_modules=["verdictos_scan"],
)
