from setuptools import setup, find_packages

setup(
    name="askos",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "askos=askos.main:main_entrypoint",
        ],
    },
)
