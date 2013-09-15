"""Vintage Numbers plugin for Sublime Text.

This module provides two command classes: :class:`ViIncrementNumberCommand` and
:class:`ViDecrementNumberCommand`.
Both are subclasses of :class:`ViNumberMixin` which implements the whole plugin
functionality, they just decide what to do with the number -- to increment or
to decrement.

"""

__version__ = '1.0.0'

import re

import sublime
import sublime_plugin


#: A compiled regular expression matching int, hex, bin and oct numbers.
NUMBER_RE = re.compile(
    r'(-?0[0-7]+)|'           # oct
    r'(-?0[xX][\da-fA-F]+)|'  # hex
    r'(-?0b[01]+)|'           # bin
    r'(-?\d+)'                # int
)


class ViNumberMixin(object):

    """A mixin for incrementing and decrementing commands.

    Implements finding all caret positions and numbers next to them, and
    converting these numbers to a proper type (int, hex, bin, oct).

    The only thing subclasses must implement is :meth:`update_int` method.

    The number will be updated if it's placed at the caret or after but still
    in the same line.  Caret will be moved to the last character of the number
    after the update.

    Example with caret before the number::

        Before: foo 9 bar
                 ^
        After:  foo 10 bar
                     ^

    Example with caret at the number::

        Before: foo 0xff bar
                     ^
        After:  foo 0x100 bar
                        ^

    """

    def __init__(self, view):
        self.view = view

    def run(self, edit):
        """Run the command.

        Find all caret positions, update numbers and at the end move carets to
        the right place.

        :param edit:
            :class:`sublime.Edit` instance.

        """
        new_regions = []
        for region in reversed(self.view.sel()):
            new_region = self.run_for_caret(edit, region)
            if new_region is not None:
                new_regions.append(new_region)
        if new_regions:
            self._update_carets(new_regions)

    def run_for_caret(self, edit, region):
        """Find and update first number after a caret in the given region.

        The first number at or after the caret will be incremented or
        decremented and then the caret will be moved to the last character of
        the number.

        Return ``None`` if:

        * there's a selection in the region
        * line is empty
        * there's no number at or after the caret

        Otherwise return :class:`sublime.Region` with new position for the
        caret.

        :param edit:
            :class:`sublime.Edit` instance.
        :param region:
            :class:`sublime.Region` instance of the selection where the caret
            is currently placed.

        """
        if not region.empty():
            return

        # Get caret position and line at the caret.
        line_no, column_no = self.view.rowcol(region.begin())
        line = self._get_line(line_no)
        if not line:
            return

        # Find first oct, hex or dec number in the line.
        number_position = self._find_first_number(line, column_no)
        if number_position is None:
            return
        # Found a number after the current caret position -- extract it
        # from the line.
        beg, end = number_position
        number = line[beg:end]

        # Apply increment/decrement command to the number.
        new_number = self.update_number(number)

        # Replace number with the incremented/decremented one.
        replace_region = self._get_replace_region(region, column_no, beg, end)
        self.view.replace(edit, replace_region, new_number)

        # Count new region to move the caret to the end of the number.
        new_region = self._get_new_region(replace_region, new_number)
        return new_region

    def update_number(self, number):
        """Update the string number of any type -- increment it or decrement.

        * Define the number type (int, hex, etc.)
        * Convert it to an integer
        * Increment or decrement by 1
        * Convert it back to its original type
        * Return the string representation of the updated number

        :param number:
            String number to update.

        """
        number_type, base = self._define_number_type_and_base(number)
        int_number = int(number, base)
        new_number = self.update_int(int_number)
        converted = str(number_type(new_number))
        return converted

    def update_int(self, number):
        """Increment or decrement an integer.

        This method must be implemented by subclasses.

        :param number:
            Number of int type.

        """
        raise NotImplementedError()

    def _get_line(self, number):
        """Return contents of a line with the given number.

        :param number:
            Line number.

        """
        char_offset = self.view.text_point(number, 0)
        line_region = self.view.line(char_offset)
        line_contents = self.view.substr(line_region)
        return line_contents

    def _find_first_number(self, line, column):
        """Find position of the first number in the line, after the caret.

        If there's any number matching :data:`NUMBER_RE` after the given
        column, return 2-tuple: number of column where the matched number
        starts and number of column where it ends.
        Otherwise return ``None``.

        :param line:
            Line contents.
        :param column:
            Number of caret position column.

        """
        matches = NUMBER_RE.finditer(line)
        for match in matches:
            beg, end = match.span()
            if end > column:
                return beg, end

    def _define_number_type_and_base(self, number):
        """Define type and integer base for a number.

        Base is used to convert number of any type to an integer before
        incrementing or decrementing, and type is used to convert it back to
        its original type.

        Return 2-tuple: type and base.  Possible return values:

        * :py:class:`int`, ``10``
        * :py:class:`hex`, ``16``
        * :py:class:`bin`, ``2``
        * :py:class:`oct`, ``8``

        :param number:
            String number, can be negative.

        """
        unsigned = number[1:] if number[0] == '-' else number
        if unsigned == '0' or unsigned[0] != '0':
            number_type = int
            base = 10
        elif unsigned[1] in ('x', 'X'):
            number_type = hex
            base = 16
        elif unsigned[1] == 'b':
            number_type = bin
            base = 2
        else:
            number_type = oct
            base = 8
        return number_type, base

    def _get_replace_region(self, caret_region, column_no, beg, end):
        """Get region containing the number to replace it with the updated one.

        Return :class:`sublime.Region`.

        :param caret_region:
            :class:`sublime.Region` with the current caret position.
        :param column_no:
            Number of the current caret position column.
        :param beg:
            Number of column where the number starts.
        :param end:
            Number of column where the number ends.

        """
        a = caret_region.b + (beg - column_no)
        b = caret_region.b + (end - column_no)
        return sublime.Region(a, b)

    def _get_new_region(self, replace_region, new_number):
        """Get region for new caret position after replace.

        Return :class:`sublime.Region` with position at the last character of
        the new number.

        :param replace_region:
            :class:`sublime.Region` which was replaced with the new number.
        :param new_number:
            The updated number as string.

        """
        number_end = replace_region.a + len(new_number) - 1
        return sublime.Region(number_end, number_end)

    def _update_carets(self, regions):
        """Update carets positions after incrementing or decrementing numbers.

        Clear all cursors and add each from the given list.

        :param regions:
            List of :class:`sublime.Region` instances with new caret
            positions to add.

        """
        carets = self.view.sel()
        carets.clear()
        for region in regions:
            carets.add(region)


class ViIncrementNumberCommand(ViNumberMixin, sublime_plugin.TextCommand):

    """Increments number at or after the caret in Vintage command mode."""

    def update_int(self, number):
        """Return the given integer incremented by 1.

        :param number:
            Number of int type.

        """
        return number + 1


class ViDecrementNumberCommand(ViNumberMixin, sublime_plugin.TextCommand):

    """Decrements number at or after the caret in Vintage command mode."""

    def update_int(self, number):
        """Return the given integer decremented by 1.

        :param number:
            Number of int type.

        """
        return number - 1
