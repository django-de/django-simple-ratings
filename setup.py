import ast
import codecs
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


setup(
    name='django-simple-ratings',
    version=find_version('ratings', '__init__.py'),
    description='a simple, extensible rating system.',
    long_description=read('README.rst'),
    author='Charles Leifer',
    author_email='coleifer@gmail.com',
    maintainer='Deutscher Django Verein e. V.',
    maintainer_email='kontakt@django-de.org',
    url='http://github.com/django-de/django-simple-ratings/tree/master',
    packages=find_packages(),
    package_data={
        'ratings': [
            'tests/fixtures/*.json',
            'tests/templates/*.html',
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
