from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chess-coordinates-trainer",
    version="0.2",
    author="Nicolas Schneider",
    description="An interactive chess coordinates training application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chess-coordinates-trainer",
    package_dir={"": "src"},  # Tells setuptools that packages are under src directory
    packages=find_packages(where="src"),  # Modified to look in src directory
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Topic :: Games/Entertainment :: Board Games",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chess-trainer=src.main:main",
        ],
    },
    package_data={
        "": [
            "assets/images/*.png",
            "docs/*.md",
        ],
    },
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    test_suite="tests",
)