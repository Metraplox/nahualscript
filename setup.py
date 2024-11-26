from setuptools import setup, find_packages

setup(
    name="nahualscript",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ply>=3.11",
    ],
    entry_points={
        "console_scripts": [
            "nahual=nahual.__main__:main",
        ],
    },
    python_requires=">=3.8",
)