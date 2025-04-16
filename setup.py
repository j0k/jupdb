from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jupdb",
    version="0.1.0",
    author="Yuri Konoplev",
    author_email="juri.konoplev@gmail.com",
    description="Jupyter-integrated Python debugger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j0k/jupdb",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyzmq>=22.3.0",
        "ipython>=8.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
