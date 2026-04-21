from setuptools import setup, find_packages

setup(
    name="wikihow",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "seleniumbase",
        "nameparser",
        "transformers",
        "pillow",
        "rich",
        "matplotlib",
        "pandas",
        "numpy"
    ],
)
