from setuptools import setup, find_packages
from easy_chain import version

with open("README.md", "r") as file_:
    long_description = file_.read()

with open("requirements.txt", "r") as file_:
    requirements = file_.read().split()

setup(
    name='easy_chain',
    version=version,
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
    install_requires=requirements,
    scripts=['easy_chain_cli',
             'utils/ganache_tools']
)
