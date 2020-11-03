from setuptools import setup, find_packages
from os.path    import dirname, abspath

base_dir = dirname(abspath(__file__))

with open(base_dir + "/README.md", "r") as file_:
    long_description = file_.read()

with open(base_dir + "/requirements.txt", "r") as file_:
    requirements = file_.read().split()

with open(base_dir + "/easy_chain/version.txt", "r") as file_:
    version = file_.read().split()[0]

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
        "easy_chain": ["version.txt",
                       "data/contracts/*.json",
                       "data/contracts/*.abi",
                       "data/contracts/*.bin",
                       "data/conf/*.json"]
    },
    python_requires='>=3.6',
    install_requires=requirements,
    scripts=['easy_chain_cli',
             'utils/ganache_tools']
)
