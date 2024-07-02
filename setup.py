""" SwanSDK setup code """
 
from setuptools import setup, find_packages
 
 
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setup(
        name="swan-sdk",
        version="0.0.3.post1",
        packages=['swan', 'swan.api', 'swan.common', 'swan.contract', 'swan.object', 'swan.contract.abi'],
        # package_data={'swan.contract.abi': ['swan/contract/abi/PaymentContract.json', 'swan/contract/abi/SwanToken.json']},
        include_package_data=True,
        description="A python developer tool kit for Swan services.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/swanchain/python-swan-sdk",
        author="SwanCloud",
        author_email="swan.development@nbai.io",
        license="MIT",
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
        ],
        install_requires=[
            "requests==2.28.1",
            "requests-toolbelt==0.10.1",
            "web3==6.15.1",
            "tqdm==4.64.1"
            ],
        entry_points={
            # placeholder
        },
        )