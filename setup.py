import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ali-cli",
    version="0.0.1",
    author="Léon Rodenburg",
    author_email="lrodenburg@xebia.com",
    description="Wraps the Alibaba Cloud SDK to make complicated tasks a lot simpler.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonrodenburg/ali-cli",
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
    entry_points={"console_scripts": ["ali = ali.cli:safe_cli"]},
)
