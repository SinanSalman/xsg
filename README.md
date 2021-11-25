# README #

## OVERVIEW ##
The X-Supply Game (**XSG**) is an educational simulation game used to help participants explore the dynamics of real supply chains. The game is a team-based multi-player online simulation where each player take on the role of managing a virtual station in a simple supply chain. The game is played in turns, in which players analyze weekly standing of their stations and decide on orders to suppliers and shipment to customers. At the end of the game, individual and team performances are analyzed and discussed in groups.
XSG is influenced by previous supply chain management games, such as the beer game and the wood supply game, but it introduces several new concepts, including:

* Configurable supply chain design
* Ordering/Shipping decisions
* Ordering/Shipping capacities
* Triple-bottom-line objectives
* Transportation environmental/monetary impact

Other features include:
* Multi-platform compatibility
* Open source

The **XSG** name comes from the game ability to be configured in various supply chain designs, allowing it to model almost any "X" supply chain.

## User Manual

The [User Manual](./docs/UserManual.MD) includes detailed instructions on player and instructor screens, XSG installation, and server administration. It also includes several screenshots showcasing the use of XSG.

## Test Drive XSG ##
You can use XSG on the following website, which is generously hosted by Zayed University:
[ZU's XSG](https://istm.zu.ac.ae/xsg).

## Source Code ##
The source distribution contains Python, JavaScript, CSS, HTML code, in addition to a sample of supply chain game designs, including: the root-beer game and the wood supply game. The code makes use of several libraries including Python-Flask, jQuery, AlpacaJs, charts.js, and vis.js. The game analytical engine is written exclusively in Python.
Source code available at: [GitHub](https://github.com/SinanSalman/xsg)

## Contribute ##
Code submissions are greatly appreciated and highly encouraged. Please send fixes, enhancements, etc. to SinanSalman at GitHub or sinan\[dot\]salman\[at\]zu\[dot\]ac\[dot\]ae.

## License ##
XSG is released under the GPLv3 license, which is available at [GNU](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Disclaimers ##
*   XSG uses Google analytics to measure its use.
*   Every game includes an expiry parameter to keep the server from crowding. When a game expires its setup and data are automatically erased. You may choose to export your game setup file to keep on your computer, however, game player data cannot be exported.
*   Games and/or games player data may also be lost due to upgrades or new feature introductions. You may export your game setup file and take screen shots of the game results to keep on your computer.

## Version History
*   Nov 11th, 2021    v0.16, edit UserManual; add TOC & update publications
*   Aug 14th, 2019    v0.15, add UserManual
*   Jun 21st, 2018    v0.14b, Major revision, includes:
      * change max customer/supplier nodes per station 3 -> 4
      * change production_min/max/limits -> order_min/max/limits
      * add ship_min/max/limits
      * add browser compatibility check in index.html
      * add optional game script
      * add two HARD Game templates to replace HRD
      * add configurable: screen refresh delays & number of games monitored
      * add [Toggle Auto-Decisions] button in game setup edit screen
      * add [Toggle Visible Stations] button in game results screen
      * add cost/fulfilment/green score graphs to game results screen
      * add cost/fulfilment/green score graphs to multi-game competition screen
      * add link to game results on multi-game competition screen
      * change behavior for multi-game competition screen; no password = read-only
      * add improved tab/focus behavior in player screen
      * fixed timer issue when client computer time is set incorrectly
      * add stations.py report warnings/errors to WGUI
      * add publications in About page
      * add [<= Go Back] link in layout.HTML
      * improved network rendering settings
      * moved palette.js to CDN
      * several bug fixes, CSS style and HTML improvements
*   Mar 19th, 2018    v0.13b, fix: station names w/period, enlarge order/shipment input box, OSG setup. add: html meta tags, robots.txt. remove: admin server shutdown function
*   Mar  1st, 2018    v0.12b, fix: expired game kill logic
*   Feb 28th, 2018    v0.11b, add: favicon.ico, secret_key configuration, disclaimers, and test drive link
*   Feb 22nd, 2018    v0.10b, add: multi-game monitor, create/edit games, timer, game expiry  
*   Oct 05th, 2017    v0.00,  Initial release

## Copyright
2017-2022 Sinan Salman, PhD.
