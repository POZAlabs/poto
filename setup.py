from setuptools import setup, find_packages

setup(
    name='poto',
    version='0.2',
    description='boto3 wrapper for deep learning',
    url='https://github.com/pozalabs/poto',
    author='Koomook',
    author_email='contact@pozalabs.com',
    license='Unlicense',
    packages=find_packages()
    install_requires=[
        'boto3',
        'numpy',
    ],
    # setup_requires=["pytest-runner"],
    # tests_require=["pytest"],
    # include_package_data=True,
    zip_safe=False
)
