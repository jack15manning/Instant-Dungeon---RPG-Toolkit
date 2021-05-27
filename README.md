# Instant Dungeon - RPG Toolkit

Table of contents
-----------------

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#acknowledgments)


Introduction
------------

Instant Dungeon is a web-based RPG Toolkit which allows users to create Dungeon Maps for table-top role-playing games such as Dungeons & Dragons. This project was created for my Third-Year University project and was developed alongside Dr James Mapp. The service allows users to fill in a number of parameters, and rapidly create a Dungeon plan which they can use for their table-top games. Unlike most other RPG Toolkit systems, Instant Dungeon also allows for the population of the Dungeon with enemies which can be grouped into a particular type - such as beasts or undead - and can be leveled appropriately for a given player party.


Installation
------------

Several libraries are required to use Instant Dungeon and can be installed using the following commands in the command line:
* PIL
```bash
pip install --upgrade Pillow
```
* Numpy + Scipy
```bash
pip install --user numpy scipy
```
* PDFKit
```bash
pip install pdfkit
```
* Flask
```bash
pip install Flask
```
* WTForms
```bash
pip install WTForms
```

After installing the required dependencies, Instant Dungeon can be ran locally by using the following steps:
1. Clone this directory to your machine
2. Open a Powershell terminal in the downloaded folder
3. Run the Flask server using the following command:
```bash
python .\server.py
```
4. Navigate to http://127.0.0.1:5000/

 
Usage
-----

### Creating a new Dungeon
1. From the Home page, fill in the Dungeon Layout and Population parameters as desired - or leave them as they are for a random Dungeon with the default settings.
2. Click the **Create** buton found at the bottom of the page.
3. Sit back and watch as your Dungeon is created for you.
4. Make note of the Dungeon Seed and Population Seed, as these can be used to recreate a previously generated Dungeon if it is lost.

### Recreating a previously generated Dungeon
1. From the Home page, fill in the Dungeon Layout and Population parameters as they were for the Dungeon you want to recreate.
2. Enter the saved Dungeon Seed and Population Seed into their respective boxes.
3. Click the **Create** button found at the bottom of the page.

### Re-populating an existing Dungeon with different enemies
1. From the Dungeon page, locate the **Re-populate** section.
2. Enter your desired parameters into the form.
3. Click the **Create** button found at the bottom of the page.

### Exporting a Dungeon Map
1. From the Dungeon Page, click the **Export to PDF** button found below the Dungeon image and Room information.
2. Open the PDF file in your chosen program after it has been downloaded to your device.


Known issues and limitations
----------------------------

**Limitations**
* Currently Instant Dungeon only supports the population of Dungeons with enemies from Dungeons & Dragons 5th Edition.

**Known Issues**
* Creating a *Tiny* sized Dungeon with a *Rectangular* shape often results in a Dungeon being created with only two rooms.


Getting help
------------

If you have any issues with using the service, please send me an email at jack15manning@gmail.com

Contributing
------------

If you would like to make any changes to my system, clone the repository and make any additions you would like. Some aspects of the system have been created in an expandable way such that they are easily added to.

Authors and history
---------------------------

Instant Dungeon was created by myself (Jack Manning) alongside Dr James Mapp as part of my Third-year University project at The University of East Anglia.


Acknowledgments
---------------

I would like to give a special thanks to Dr James Mapp for supervising my project and providing me with solutions whenever problems arose. Listed below are a number of sources which were used during the development of my project.

* 
* https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
* https://guides.github.com/features/mastering-markdown/
