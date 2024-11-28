# setup.py
from setuptools import setup, find_packages

setup(
    name="lizard_requests",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pydantic"
    ],
    author="Nelen & Schuurmans",
    author_email="servicedesk@nelen-schuurmans.com",
    description="A package to use the Lizard API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypackage",  # Replace with your package's URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
