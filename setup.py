from setuptools import setup, find_packages

setup(
    name="alfacrm",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
