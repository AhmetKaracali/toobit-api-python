from setuptools import setup, find_packages

setup(
    name='toobit-api-python',
    version='0.1.0',
    author='Ahmet KARAÇALI',
    author_email='akaracali58@gmail.com',
    packages=find_packages(),
    description='Python client for the TooBit Exchange Trading API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AhmetKaracali/toobit-api-python',
    install_requires=['requests'],
    classifiers=[
        # Classifier'lar için: https://pypi.org/classifiers/
    ],
)