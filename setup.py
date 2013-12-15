from distutils.core import setup

requires = ['docopt', 'fuzzywuzzy', 'pyxdg']

setup(
    name='jay',
    version='0.1',
    description='A command line tool for quickly jumping around your filesystem.',
    license='MIT',
    long_description='A command line tool for quickly jumping around your filesystem.',
    author='hernantz',
    author_email='hernantz@gmail.com',
    entry_points = {
        'console_scripts': ['jay = jay:main']
    },
    packages=['jay'],
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
