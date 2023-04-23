import os

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    print('Being built on ReadTheDocs so we are avoiding pulling in scikit-bio since it imports numpy...')
    requirements = []
else:
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

setup(
    name='pyLDAvis',
    version='3.4.1',
    description='Interactive topic model visualization. Port of the R package.',
    long_description_content_type="text/x-rst",
    long_description=readme,
    author='Ben Mabey',
    author_email='ben@benmabey.com',
    url='https://github.com/bmabey/pyLDAvis',
    download_url='https://github.com/bmabey/pyLDAvis/tarball/3.4.1',
    packages=['pyLDAvis'],
    package_dir={'pyLDAvis': 'pyLDAvis'},
    tests_require=['pytest'],
    python_requires=">=3.9",
    include_package_data=True,
    install_requires=requirements,
    license='BSD-3-Clause',
    zip_safe=False,
    keywords=['data science', 'visualization'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)