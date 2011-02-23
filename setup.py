import os
from setuptools import setup, find_packages

from ratings import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-simple-ratings',
    version=".".join(map(str, VERSION)),
    description='a simple, extensible rating system.',
    long_description=readme,
    author='Charles Leifer',
    author_email='coleifer@gmail.com',
    url='http://github.com/coleifer/django-simple-ratings/tree/master',
    packages=find_packages(),
    package_data = {
        'ratings': [
            'tests/fixtures/*.json',
        ],
    },
    install_requires=['django-generic-aggregation'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    test_suite='runtests.runtests',
)
