======================================
Vintage Numbers: a Sublime Text plugin
======================================

Allows you to increment and decrement numbers in Vintage command mode using the
same key bindings as in Vi.

Works with decimal, hexadecimal, binary and octal numbers.


Using
=====

* Use ``ctrl+a`` to increment a number
* Use ``ctrl+x`` to decrement a number


Installation
============

The recommmended method of installation is via **Package Control**.
It will download upgrades automatically.

Package Control
---------------

* Follow instructions on https://sublime.wbond.net/installation
* Install using ``Package Control: Install`` > ``Vintage Numbers package``

Using Git
---------

Go to your Sublime Text Packages directory and clone the repository using the
command below::

    $ git clone https://github.com/ignacysokolowski/SublimeVintageNumbers "VintageNumbers"

Download Manually
-----------------

* Download the files using the Github downloads option
* Unzip/untar the files and rename the folder to **VintageNumbers**
* Copy the folder to your Sublime Text Packages directory


Changelog
=========

1.0.0
-----

* Initial release


Contributing
============

* Follow PEP-8 rules
* Follow PEP-257 rules
* Follow The Zen of Python
* Test your commits

Testing
-------

Tests can be run from Sublime Text console.

Open the console using ``ctrl+``` shortcut or the ``View > Show Console`` menu.
Once open, paste this Python code into the console::

    import vintage_numbers_tests; vintage_numbers_tests.run()
