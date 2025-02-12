from pathlib import Path

import setuptools

here = Path(__file__).parent.resolve()

with open(here / "requirements.txt", encoding="utf-8") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="autoppia_iwa",
    version="0.0.1",
    description="A short description of the autoppia_iwa package",
    packages=["autoppia_iwa"],
    install_requires=required,
    python_requires=">=3.11",
)
