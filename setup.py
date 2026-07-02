from setuptools import setup, find_packages

setup(
    name="agent-chaos-framework",
    version="1.0.0",
    author="Keyur Bele",
    description="A testing tool for exploring congestion and fault propagation in asynchronous systems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/keyurbele",  # Replace with your actual repo link
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
)
