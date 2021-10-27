"""m-Bitbeam online catalog project."""
from distutils.errors import DistutilsError
from os import walk

from setuptools import setup
from setuptools.command.test import test

from bitbeam_catalog import __version__

# environ.update({'PYTHONPATH': 'bitbeam_catalog'})

REQUIRES = []
with open("requirements.txt", "r") as requires:
    for line in requires:
        REQUIRES.append(line.strip())


def find_data_files(directory, target_folder=""):
    """Find files in directory, and prepare tuple for setup."""
    rv = []  # pylint: disable=C0103
    for root, dirs, files in walk(directory):  # pylint: disable=W0612
        if target_folder:
            rv.append((target_folder + root[len(directory):],
                       list(root + '/' + f for f in files
                            if f[0] != '.' and f[-1] != '~')))
        else:
            rv.append((root,
                       list(root + '/' + f for f in files
                            if f[0] != '.' and f[-1] != '~')))
    return rv


class PyTest(test):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test.'),
                    ('test-suite=', 't', 'Test suite/module::Class::test')]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        test.finalize_options(self)
        if isinstance(self.pytest_args, (str)):
            self.pytest_args = self.pytest_args.split(' ')

        self.pytest_args.append(self.test_suite or 'tests')
        if self.verbose:
            self.pytest_args.insert(0, '-v')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        if pytest.main(self.pytest_args) != 0:
            raise DistutilsError("Test failed")


def doc():
    """Return README.rst content."""
    with open('README.rst', 'r') as readme:
        return readme.read().strip()


setup(
    name="m-Bitbeam Catalog",
    version=__version__,
    description="On-line catalog for m-bitbeam repository",
    author="Ondřej Tůma",
    author_email="mcbig@zeropage.cz",
    maintainer="Ondrej Tuma",
    maintainer_email="mcbig@zeropage.cz",
    url="https://m-bitbeam.geekzoo.cz",
    packages=['bitbeam_catalog'],
    include_package_data=True,
    data_files=[('share/doc/bitbeam_catalog', [
        'doc/ChangeLog', 'doc/licence.txt', 'README.rst', 'CONTRIBUTION.rst'
    ]),
                ('share/bitbeam_catalog/examples',
                 ['etc/uwsgi.ini', 'etc/application.ini'])] +
    find_data_files("web", "share/bitbeam_catalog/web"),
    license="BSD",
    long_description=doc(),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Customer Service",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    python_requires=">=3",
    install_requires=REQUIRES,
)
