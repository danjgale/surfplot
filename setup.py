from setuptools import setup, find_packages
import re
import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('brainplot/__init__.py', encoding='utf_8_sig').read()
    ).group(1)

test_deps = ['pytest-cov',
             'pytest']

extras = {
    'test': test_deps,
}

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='brainplot',
    version=__version__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    license='BSD-3',
    author='Dan Gale',
    maintainer_email="d.gale@queensu.ca",
    description=("A high-level interface for Brainspace's surface plotting "
                 "capabilities"),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/danjgale/brainplot',
    python_requires='>=3.7.0',
    install_requires=[
            'brainnotation',
            'brainspace>=0.1.1',
            'matplotlib>=3.2.0',
            'nibabel',
            'nilearn>=0.7.0',
            'numpy>=1.14.0',
            'scipy>=0.17',
            'vtk>=8.1.0'
    ],
    package_data={
        'brainplot': ['data/*']
    },
    include_package_data=True,
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=['pytest-runner'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering'
    ]
)
