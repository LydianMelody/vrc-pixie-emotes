from setuptools import setup, find_packages

setup(
    name="vrc-pixie",
    version="1.0.0",
    description="Convert GIFs into VRChat-compatible sprite sheets",
    author="LydianMelody",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "Pillow==10.1.0",
        "imageio==2.33.0", 
        "numpy==1.24.3",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pixie=main:main',
            'pixie-cli=quick_start:main',
        ],
    },
)
