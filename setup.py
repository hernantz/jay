import sys
from distutils.core import setup


requires = ['docopt', 'fuzzywuzzy', 'pyxdg', 'future']
if sys.version_info.major < 3:
    requires += ['unicodecsv']  # use only in python2.x


setup(
    name='jay',
    version='0.2',
    description='A command line tool for quickly jumping around your filesystem.',
    license='MIT',
    long_description='A command line tool for quickly jumping around your filesystem.',
    author='hernantz',
    author_email='hernantz@gmail.com',
    install_requires=requires,
    entry_points = {
        'console_scripts': ['jay = jay:main']
    },
    packages=['jay'],
    package_data = {'jay': ['jay.bash', 'jay-autocomplete.bash']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: MIT',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
