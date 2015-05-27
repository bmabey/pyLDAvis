#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

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

requirements = [
    'pandas',
    'numexpr',
    'numpy',
    'funcy',
    'jinja2==2.7.2',
    'scikit-bio==0.2.3',
    'joblib==0.8.4'
]

test_requirements = [
    'pytest',
    'funcy'
]

setup(
    name='pyLDAvis',
    version='0.1.0',
    description="Python package for interactive topic model visualization. Port of the R package.",
    long_description=readme + '\n\n' + history,
    author="Ben Mabey",
    author_email='ben@benmabey.com',
    url='https://github.com/bmabey/pyLDAvis',
    packages=[
        'pyLDAvis',
    ],
    package_dir={'pyLDAvis':
                 'pyLDAvis'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='pyLDAvis',
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
