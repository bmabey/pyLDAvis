#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    from distutils.core import setup
    from distutils.core.command.test import test as TestCommand


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

# via https://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    print('Being built on ReadTheDocs so we are avoiding pulling in scikit-bio since it imports numpy...')
    requirements = []
else:
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()


test_requirements = [
    'pytest',
    'funcy'
]

setup(
    name='pyLDAvis',
    version='1.3.5',
    description="Interactive topic model visualization. Port of the R package.",
    long_description=readme + '\n\n' + history,
    author="Ben Mabey",
    author_email='ben@benmabey.com',
    url='https://github.com/bmabey/pyLDAvis',
    download_url = 'https://github.com/bmabey/pyLDAvis/tarball/1.2.0',
    packages=[
        'pyLDAvis',
    ],
    package_dir={'pyLDAvis':
                 'pyLDAvis'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords=['data science', 'visualization'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass = {'test': PyTest}
)
