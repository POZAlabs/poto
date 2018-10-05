from setuptools import setup, find_packages

setup(
    name='poto',
    version='1.0.2',
    description='boto3 wrapper for deep learning',
    url='https://github.com/pozalabs/poto',
    author='Koomook',
    author_email='contact@pozalabs.com',
    license='Unlicense',
    packages=['poto',],
    install_requires=[
        'boto3',
        'numpy',
    ],
    # setup_requires=["pytest-runner"],
    # tests_require=["pytest"],
    include_package_data=True,
    zip_safe=False
)
