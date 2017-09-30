# README #

**XSG**

## OVERVIEW ##
The X-Supply Game (**XSG**) is an educational simulation game used to help participants explore the dynamics of a real supply chains. The game is a team-based multi-player online simulation where each player take on the role of managing a virtual station in a simple supply chain. The game is played in turns, in which players analyze weekly standing of their stations and decide on orders to suppliers and shipment to customers. At the end of the game, individual and team performances are analyzed and discussed in groups.
XSG is influenced by previous supply chain management games, such as the beer game and the wood supply game, but it introduces several new concepts, including:

* **Configurable supply chain design**: the simulated simple supply chain can be of virtually any design; number of nodes, number of layers, number of suppliers/customers per node (although this is currently limited to two for user interface simplicity).
* **Production capacity**: any station (node) can have an arbitrary weekly production minimums/maximums.
* **Triple-bottom-line objective**: previous games focused on cost and/or service level as performance metrics for the game. XGS extends this with an environmental objective to require the player to consider all three objectives while making turn decisions. This is incorporated through the shipping decision, as explained in the transportation point below.
* **Transportation environmental/monetary**: a game can be configured to require players to consider either, or both ordering (from suppliers) and shipping (to customers) decisions. In the latter case, an environmental impact based on truck utilization results and necessitate that the player make decisions on order deferment or partial shipping to minimize the environmental impact. In addition, a transportation cost results, allowing the players to fully engage in triple bottom line evaluation.

Other features include:
* Multi-platform compatibility: XSG can be accessed from any modern computing device with a browser capable of supporting JavaScript, which includes almost all personal computers, tablets, and mobile devices. In addition, the server supports computing platforms where Python and Flask are available.
* Open source: XSG is open sourced (see license section below)

The **XSG** name comes from the game ability to be configured in various supply chain designs, allowing it to model almost any "X" supply chain.

## Installation ##
XSG can be installed as a python package using the following command  (on OSX/Linux):

'''pip install xsg'''

and to start the server, use:
'''cd xsg
./srart.sh'''

Windows installation and use was not tested but should follow similar steps.

## SOURCE CODE ##
The source distribution contains Python, JavaScript, CSS, HTML code, in addition to a sample of supply chain game designs, including: the root-beer game, the wood supply game. The code makes use of several libraries including Python-Flask, jQuery, charts.js, and vis.js. The game analytical engine is written exclusively in Python.

## CONTRIBUTE	##
Code submissions are greatly appreciated and highly encouraged. Please send fixes, enhancements, etc. to sinan[dot]salman[at]zu.ac.

## LICENSE	##
XSG is released under the GPLv3 license, which is available at:
https://www.gnu.org/licenses/gpl-3.0.en.html

## COPYRIGHT	##
2017 Sinan Salman, PhD

## Version and History ##
Sep 28th, 2017		Initial release
