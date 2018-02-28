# README #

## OVERVIEW ##
The X-Supply Game (**XSG**) is an educational simulation game used to help participants explore the dynamics of real supply chains. The game is a team-based multi-player online simulation where each player take on the role of managing a virtual station in a simple supply chain. The game is played in turns, in which players analyze weekly standing of their stations and decide on orders to suppliers and shipment to customers. At the end of the game, individual and team performances are analyzed and discussed in groups.
XSG is influenced by previous supply chain management games, such as the beer game and the wood supply game, but it introduces several new concepts, including:

*   **Configurable supply chain design**: the simulated simple supply chain can be of virtually any design; number of nodes, number of layers, number of suppliers/customers per node (although this is currently limited to two for user interface simplicity). The only exception is supply chains containing closed-loop.
*   **Production capacity**: stations (or SC nodes) can have weekly production minimums/maximums.
*   **Triple-bottom-line objective**: previous games focused on cost and/or service level as performance metrics for the game. XGS extends this with an environmental objective to require the player to consider all three objectives while making turn decisions. This is incorporated through the shipping decision, as explained in the transportation point below.
*   **Transportation environmental/monetary**: a game can be configured to require players to consider either, or both ordering (from suppliers) and shipping (to customers) decisions. In the latter case, an environmental impact based on truck utilization results and necessitate that the player make decisions on order deferment or partial shipping to minimize the environmental impact. In addition, a transportation cost results, allowing the players to fully engage in triple bottom line evaluation.

Other features include:

*   Multi-platform compatibility: XSG can be accessed from any modern computing device with a browser capable of supporting JavaScript, which includes almost all personal computers, tablets, and mobile devices. In addition, the server supports computing platforms where Python and Flask are available, including: OSX, Linux, and Windows among others.
*   Open source: XSG is open sourced (see license section below)

The **XSG** name comes from the game ability to be configured in various supply chain designs, allowing it to model almost any "X" supply chain.

## Screen shots ##
You can see various XSG screenshots on the following link:
[XSG screen shots](https://sinansalman.github.io/xsg/docs/screenshots.html)

## Test Drive XSG ##
You can use XSG on the following website, which is generously hosted by Zayed University:
[ZU's XSG](https://istm.zu.ac.ae/xsg)

## Installation ##
You may install XSG on your computer as a python3 package to test it:

*   Clone the project's repository or download its zip file from [github.com](https://sinansalman.github.io/xsg/)
*   Unzip the file to a folder on your hard drive and rename the resulting folder to 'xsg'
*   Install the python package and start it

The following was tested on MacOS with a new anaconda environment initialized to python 3.6:

```
git clone https://github.com/SinanSalman/xsg.git
cd xsg
pip install .
./start_in_debug_mode.sh
```

Windows installation and use was not tested but should follow similar steps. To install the package for development purposes use: ```pip install -e .```

You may also install XSG on Web server. The following tutorials provide help on setting up XSG (a Flask application) as a WSGI application on an Apache server:
*   [DigitalOcean's tutorial on serving flask applications with uWSGI on CentOS 7](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-centos-7)
*   [How To Flask, Python, Centos7, Apache, uWSGI 7](https://mitchjacksontech.github.io/How-To-Flask-Python-Centos7-Apache-uWSGI/)

## Source Code ##
The source distribution contains Python, JavaScript, CSS, HTML code, in addition to a sample of supply chain game designs, including: the root-beer game, the wood supply game. The code makes use of several libraries including Python-Flask, jQuery, AlpacaJs, charts.js, and vis.js. The game analytical engine is written exclusively in Python.

## Contribute ##
Code submissions are greatly appreciated and highly encouraged. Please send fixes, enhancements, etc. to SinanSalman at GitHub or sinan\[dot\]salman\[at\]zu\[dot\]ac\[dot\]ae.

## License ##
XSG is released under the GPLv3 license, which is available at [GNU](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Disclaimers ##

*   XSG uses Google analytics to measure its use.
*   Every game includes an expiry parameter to keep the server from crowding. When a game expires its setup and data are automatically erased. You may choose to export your game setup file to keep on your computer, however, game player data cannot be exported.
*   Games and/or games player data may also be lost due to upgrades or new feature introductions. You may export your game setup file and take screen shots of the game results to keep on your computer.

## Copyright ##
2017 Sinan Salman, PhD

## Version and History ##
*   Oct 05th, 2017    Initial release
*   Feb 22nd, 2018    v0.1b, add: multi-game monitor, create/edit games, timer, game expiry  
*   Feb 28th, 2018    v0.11b, add: favicon.ico, secret_key configuration, disclaimers, and test drive link
