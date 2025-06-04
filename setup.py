from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="pyward-cli",
    version="0.1.1",
    description="CLI linter for Python (optimization + security checks)",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Karan Vasudevamurthy",
    author_email="karanlvm123@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pyward=pyward.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
)
