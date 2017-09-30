from setuptools import setup

setup(
    name='xsg',
    version="0.0.1",
    license="GPLv3",
    author='Sinan Salman',
    author_email='sinan [dot] salman [at] gmail [dot] com',
    description=('X Supply chain Game (XSG) is a team based online multiplayer '
                 'game designed to help players understand the dynamics '
                 'and complexities of real supply chain systems through '
                 'simulating a small supply chain'),
    url="https://bitbucket.org/sinansalman/xsg/",
    packages=['xsg'],
    include_package_data=True,
    install_requires=['flask',],
    python_requires=">=3.6",
)
