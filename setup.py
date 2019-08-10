from setuptools import setup

setup(
    name='xsg',
    version="0.15",
    license="GPLv3",
    author='Sinan Salman',
    author_email='sinan[dot]salman[at]zu[dot]ac[dot]ae',
    description=('X Supply chain Game (XSG) is a team based online multiplayer '
                 'game designed to help players understand the dynamics '
                 'and complexities of real supply chain systems through '
                 'simulating a small supply chain'),
    url="https://sinansalman.github.io/xsg/",
    packages=['xsg'],
    include_package_data=True,
    install_requires=['flask','numpy',],
    python_requires=">=3.5",
)
