from setuptools import setup


setup(
    name='fb-sdk-py',
    version="0.0.1",                # noqa: F821
    description='This client library is designed to support the Facebook Graph API',      
    author='Caivy',
    url='https://github.com/Caivy/fb-sdk-py',
    license='Apache',
    packages=["facebook-sdk"],
    long_description=open("README.md").read(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=['requests']
)