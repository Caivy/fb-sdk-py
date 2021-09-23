from setuptools import setup


setup(
    name='facebook-sdk-py',
    version="0.0.2",             
    description='This client library is designed to support the Facebook Graph API',      
    author='Caivy',
    url='https://github.com/Caivy/fb-sdk-py',
    license='Apache',
    packages=["fbsdk"],
    long_description=open("README.md").read(),
    keywords=["python", "facebook", "API", "Faccebook Graph API", "requests"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=['requests']
)
