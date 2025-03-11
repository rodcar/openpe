from setuptools import setup, find_packages

setup(
    name='openpe',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        "requests",
        "bs4",
        "pandas",
        "tqdm",
        "openpyxl"
    ],
    author='Ivan Yang Rodriguez Carranza',
    author_email='nnrodcar@gmail.com',
    description='A library for search datasets on datosabiertos.gob.pe',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rodcar/openpe',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license="MIT",
)