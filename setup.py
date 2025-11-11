from setuptools import setup, find_packages
    
VERSION = "2.0.4"

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="pyxui_async",
    version=VERSION,
    author="Staliox, ARLIKIN",
    description="An application with python that allows you to modify your xui panel",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ARLIKIN/pyxui_async",
    keywords=[
        "pyxui async",
        "xui",
        "xui python",
        "xui panel"
    ],
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic>=2.11.7"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT"
)
