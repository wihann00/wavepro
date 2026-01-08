from setuptools import setup, find_packages

setup(
    name="wavedump-processor",
    version="1.0.0",
    packages=find_packages(),
    py_modules=['process_wavedump'],  # Include the root-level script
    install_requires=[
        "numpy>=1.20.0",
        "uproot>=4.0.0",
        "tqdm>=4.60.0",
        "setuptools>=45.0.0",
    ],
    entry_points={
        'console_scripts': [
            'wavepro=process_wavedump:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Process CAEN WaveDump files to ROOT ntuples",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
)