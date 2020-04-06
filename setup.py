import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ali-cli",
    version="0.7.3",
    author="Léon Rodenburg",
    author_email="lrodenburg@xebia.com",
    keywords="alibaba cloud aliyun cli",
    description="Wraps the Alibaba Cloud SDK to make complicated tasks a lot simpler.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonrodenburg/ali-cli",
    packages=setuptools.find_packages(exclude=("tests",)),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["ali = ali.cli:safe_cli"]},
    install_requires=[
        "click>=7.0",
        "colorama>=0.4.1",
        "pygments>=2.4.2",
        "ruamel.yaml>=0.16.5",
        "xmltodict>=0.12.0",
        "requests>=2.22.0",
        "urllib3>=1.25.3",
        "cryptography>=2.7",
        "humanize>=0.5.1",
        "aliyun-python-sdk-core>=2.13",
        "aliyun-python-sdk-ros>=2.2.8",
        "aliyun-python-sdk-kms>=2.5.0",
        "aliyun-python-sdk-sts>=3.0.1",
        "aliyun-python-sdk-cr>=3.0.1",
        "oss2>=2.8.0",
    ],
)
