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

with open("README.md", "r", encoding="utf-8") as fh:
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
        'brainspace>=0.1.1',
        'nibabel>=3.2.0',
        'nilearn>=0.7.0',
        'numpy>=1.16.5',
        'vtk'
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
