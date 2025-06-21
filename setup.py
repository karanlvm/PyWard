from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

def get_version():
    version_file = HERE / "pyward" / "__init__.py"
    for line in version_file.read_text().splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Version not found")

setup(
    name="pyward-cli",
    version=get_version(),
    description="A CLI linter for Python that flags optimization and security issues",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Karan Vasudevamurthy",
    author_email="karanlvm123@gmail.com",
    url="https://github.com/karanlvm/pyward-cli",
    project_urls={
        "Source": "https://github.com/karanlvm/pyward-cli",
        "Documentation": "https://github.com/karanlvm/pyward-cli#readme",
        "Issue Tracker": "https://github.com/karanlvm/pyward-cli/issues",
    },
    license="MIT",
    keywords="python lint cli security optimization",
    packages=find_packages(),    python_requires=">=3.7",
    include_package_data=True,
    install_requires=[
        "colorama>=0.4.6",
        "pandas>=2.3.0,<3.0.0",
    ],
    tests_require=[
        "pytest>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pyward=pyward.cli:main",
        ],
    },
    classifiers=[
        # Who your project is for
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",

        # Supported Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        # License
        "License :: OSI Approved :: MIT License",

        # Operating systems
        "Operating System :: OS Independent",
    ],
)
