from setuptools import setup, find_packages

with open("README.md", "r") as file_:
    long_description = file_.read()

setup(
    name='easy_chain',
    version='0.1.1',
    packages=find_packages(),
    author='Juan S. Bokser',
    author_email='juan.bokser@gmail.com',
    description='Python framework for blockchain projects',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    package_data={
        "easy_chain": ["data/contracts/*.json",
                       "data/contracts/*.abi",
                       "data/contracts/*.bin",
                       "data/conf/*.json"]
    },
    python_requires='>=3.6',
    install_requires=[
        'click',
        'tabulate',
        'web3'
    ],
    scripts=['easy_chain_wallet.py']
)
