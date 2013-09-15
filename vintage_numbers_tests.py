"""Tests for the plugin.

Run in Sublime Text console::

    >>> import vintage_numbers_tests; vintage_numbers_tests.run()

"""

import sys
import unittest

import sublime

import vintage_numbers


class ViNumberMixinTestCase(unittest.TestCase):

    """Unit tests for the ViNumberMixin class."""

    def setUp(self):
        self.command = vintage_numbers.ViNumberMixin(None)

    def test_find_first_number_when_no_number_in_line(self):
        line, col = 'foo bar baz', 0
        position = self.command._find_first_number(line, col)
        self.assertEqual(position, None)

    def test_find_first_number_when_before_the_caret(self):
        line, col = 'foo 1 bar', 6
        position = self.command._find_first_number(line, col)
        self.assertEqual(position, None)

    def test_find_first_number_when_at_the_caret(self):
        line, col = 'foo 1 bar 2', 4
        position = self.command._find_first_number(line, col)
        self.assertEqual(position, (4, 5))

    def test_find_first_number_when_before_and_after_the_caret(self):
        line, col = 'foo 1 bar 123 baz', 6
        position = self.command._find_first_number(line, col)
        self.assertEqual(position, (10, 13))

    def test_define_number_type_and_base_for_int_positive(self):
        no_type, base = self.command._define_number_type_and_base('123')
        self.assertEqual(no_type, int)
        self.assertEqual(base, 10)

    def test_define_number_type_and_base_for_int_negative(self):
        no_type, base = self.command._define_number_type_and_base('-123')
        self.assertEqual(no_type, int)
        self.assertEqual(base, 10)

    def test_define_number_type_and_base_for_int_0(self):
        no_type, base = self.command._define_number_type_and_base('0')
        self.assertEqual(no_type, int)
        self.assertEqual(base, 10)

    def test_define_number_type_and_base_for_hex_lowercase(self):
        no_type, base = self.command._define_number_type_and_base('0xff')
        self.assertEqual(no_type, hex)
        self.assertEqual(base, 16)

    def test_define_number_type_and_base_for_hex_uppercase(self):
        no_type, base = self.command._define_number_type_and_base('0XFF')
        self.assertEqual(no_type, hex)
        self.assertEqual(base, 16)

    def test_define_number_type_and_base_for_hex_negative(self):
        no_type, base = self.command._define_number_type_and_base('-0xff')
        self.assertEqual(no_type, hex)
        self.assertEqual(base, 16)

    def test_define_number_type_and_base_for_bin(self):
        no_type, base = self.command._define_number_type_and_base('0b1010')
        self.assertEqual(no_type, bin)
        self.assertEqual(base, 2)

    def test_define_number_type_and_base_for_bin_negative(self):
        no_type, base = self.command._define_number_type_and_base('-0b1010')
        self.assertEqual(no_type, bin)
        self.assertEqual(base, 2)

    def test_define_number_type_and_base_for_oct(self):
        no_type, base = self.command._define_number_type_and_base('012')
        self.assertEqual(no_type, oct)
        self.assertEqual(base, 8)

    def test_define_number_type_and_base_for_oct_negative(self):
        no_type, base = self.command._define_number_type_and_base('-012')
        self.assertEqual(no_type, oct)
        self.assertEqual(base, 8)

    def test_get_replace_region_when_number_is_after_the_caret(self):
        # foo bar baz
        # foo 123 baz
        caret_region = sublime.Region(14, 14)  # 3rd char in 2nd line ('o').
        col = 2  # 3rd char in 2nd line ('o').
        beg, end = 4, 6  # 5th - 7th chars in 2nd line ('123').

        region = self.command._get_replace_region(caret_region, col, beg, end)

        self.assertEqual(region, sublime.Region(16, 18))

    def test_get_replace_region_when_number_is_at_the_caret(self):
        # foo bar baz
        # foo 123 baz
        caret_region = sublime.Region(16, 16)  # 5th char in 2nd line ('1').
        col = 4  # 5th char in 2nd line ('1').
        beg, end = 4, 6  # 5th - 7th chars in 2nd line ('123').

        region = self.command._get_replace_region(caret_region, col, beg, end)

        self.assertEqual(region, sublime.Region(16, 18))

    def test_get_new_region_when_number_length_didnt_change(self):
        # Before:
        # foo bar baz
        # foo 123 baz
        # After:
        # foo bar baz
        # foo 124 baz
        replace_region = sublime.Region(16, 18)  # 5th - 7th in 2nd line (123).
        new_number = '124'

        new_region = self.command._get_new_region(replace_region, new_number)

        # Moved to the end of the number.
        self.assertEqual(new_region, sublime.Region(18, 18))

    def test_get_new_region_when_number_length_increased(self):
        # Before:
        # foo bar baz
        # foo 999 baz
        # After:
        # foo bar baz
        # foo 1000 baz
        replace_region = sublime.Region(16, 18)  # 5th - 7th in 2nd line (999).
        new_number = '1000'

        new_region = self.command._get_new_region(replace_region, new_number)

        # Number length increased from 3 to 4 -- it now ends at 19th char.
        self.assertEqual(new_region, sublime.Region(19, 19))

    def test_get_new_region_when_number_length_decreased(self):
        # Before:
        # foo bar baz
        # foo 100 baz
        # After:
        # foo bar baz
        # foo 99 baz
        replace_region = sublime.Region(16, 18)  # 5th - 7th in 2nd line (100).
        new_number = '99'

        new_region = self.command._get_new_region(replace_region, new_number)

        # Number length decreased from 3 to 2 -- it now ends at 17th char.
        self.assertEqual(new_region, sublime.Region(17, 17))


class ViIncrementNumberCommandTestCase(unittest.TestCase):

    """Tests for the ViIncrementNumberCommand class."""

    def setUp(self):
        self.command = vintage_numbers.ViIncrementNumberCommand(None)

    def test_update_number(self):
        self.assertEqual(self.command.update_number('0'), '1')
        self.assertEqual(self.command.update_number('-10'), '-9')
        self.assertEqual(self.command.update_number('101'), '102')
        self.assertEqual(self.command.update_number('0xff'), '0x100')
        self.assertEqual(self.command.update_number('0XFE'), '0xff')
        self.assertEqual(self.command.update_number('-0xff'), '-0xfe')
        self.assertEqual(self.command.update_number('0b1010'), '0b1011')
        self.assertEqual(self.command.update_number('-0b1011'), '-0b1010')
        self.assertEqual(self.command.update_number('011'), '012')
        self.assertEqual(self.command.update_number('017'), '020')
        self.assertEqual(self.command.update_number('-020'), '-017')


class ViDecrementNumberCommandTestCase(unittest.TestCase):

    """Tests for the ViDecrementNumberCommand class."""

    def setUp(self):
        self.command = vintage_numbers.ViDecrementNumberCommand(None)

    def test_update_number(self):
        self.assertEqual(self.command.update_number('0'), '-1')
        self.assertEqual(self.command.update_number('1'), '0')
        self.assertEqual(self.command.update_number('-9'), '-10')
        self.assertEqual(self.command.update_number('102'), '101')
        self.assertEqual(self.command.update_number('0x100'), '0xff')
        self.assertEqual(self.command.update_number('0XFF'), '0xfe')
        self.assertEqual(self.command.update_number('-0xfe'), '-0xff')
        self.assertEqual(self.command.update_number('0b1011'), '0b1010')
        self.assertEqual(self.command.update_number('-0b1010'), '-0b1011')
        self.assertEqual(self.command.update_number('012'), '011')
        self.assertEqual(self.command.update_number('020'), '017')
        self.assertEqual(self.command.update_number('-017'), '-020')


class IntegrationTestCase(unittest.TestCase):

    """Tests which require real view instance.

    New view is opened before each test and closed on test teardown.

    """

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()

    def tearDown(self):
        self.view.set_scratch(True)
        self.window.run_command('close')

    def assertViewContent(self, expected):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        self.assertEqual(content, expected)

    def assertRegions(self, regions_points):
        regions = [sublime.Region(beg, end) for beg, end in regions_points]
        self.assertEqual(list(self.view.sel()), regions)

    def test_get_line(self):
        self._insert(
"""\
foo bar
lorem ipsum dolor sit amet

foo baz
"""
        )
        self.window.focus_view(self.view)
        command = vintage_numbers.ViNumberMixin(self.view)

        self.assertEqual(command._get_line(0), 'foo bar')
        self.assertEqual(command._get_line(1), 'lorem ipsum dolor sit amet')
        self.assertEqual(command._get_line(2), '')
        self.assertEqual(command._get_line(3), 'foo baz')

    def test_update_carets(self):
        self.window.focus_view(self.view)
        command = vintage_numbers.ViNumberMixin(self.view)
        self._add_regions([(1, 2), (5, 5), (10, 15)])
        new_points = [(3, 3), (11, 13)]
        new_regions = [sublime.Region(*points) for points in new_points]

        command._update_carets(new_regions)

        self.assertRegions(new_points)

    def test_increment_in_view(self):
        self._insert(
"""\
-1
foo 2
foo 3 bar 9
foo 5 bar
foo 6 bar
0XFF
0xfe
-0xff
0b1010
-0b1011
011
017
-020
"""
        )
        self._add_regions([
            (0, 0),
            (3, 3),
            (15, 15),
            (27, 27),
            (31, 34),
            (41, 41),
            (46, 46),
            (51, 51),
            (57, 57),
            (64, 64),
            (72, 72),
            (76, 76),
            (80, 80),
        ])
        self._run_increment()

        self.assertViewContent(
"""\
0
foo 3
foo 3 bar 10
foo 5 bar
foo 6 bar
0x100
0xff
-0xfe
0b1011
-0b1010
012
020
-017
"""
        )
        self.assertRegions([
            (0, 0),
            (7, 7),
            (20, 20),
            (45, 45),
            (49, 49),
            (55, 55),
            (62, 62),
            (70, 70),
            (74, 74),
            (78, 78),
            (83, 83),
        ])

    def test_decrement_in_view(self):
        self._insert(
"""\
0
foo 2
foo 3 bar 10
foo 5 bar
foo 6 bar
0x100
0XFF
-0xfe
0b1011
-0b1010
012
020
-017
"""
        )
        self._add_regions([
            (0, 0),
            (2, 2),
            (14, 14),
            (26, 26),
            (30, 33),
            (41, 41),
            (47, 47),
            (52, 52),
            (58, 58),
            (65, 65),
            (73, 73),
            (77, 77),
            (81, 81),
        ])
        self._run_decrement()

        self.assertViewContent(
"""\
-1
foo 1
foo 3 bar 9
foo 5 bar
foo 6 bar
0xff
0xfe
-0xff
0b1010
-0b1011
011
017
-020
"""
        )
        self.assertRegions([
            (1, 1),
            (6, 6),
            (18, 18),
            (44, 44),
            (50, 50),
            (56, 56),
            (63, 63),
            (71, 71),
            (75, 75),
            (79, 79),
            (84, 84),
        ])

    def test_increment_in_empty_view(self):
        self._insert('')
        self._run_increment()
        self.assertViewContent('')

    def _insert(self, text, point=0):
        edit = self.view.begin_edit()
        self.view.insert(edit, point, text)
        self.view.end_edit(edit)

    def _add_regions(self, regions_points):
        for beg, end in regions_points:
            self.view.sel().add(sublime.Region(beg, end))

    def _run_increment(self):
        self._run_command(vintage_numbers.ViIncrementNumberCommand)

    def _run_decrement(self):
        self._run_command(vintage_numbers.ViDecrementNumberCommand)

    def _run_command(self, cmd_class):
        self.window.focus_view(self.view)
        command = cmd_class(self.view)
        edit = self.view.begin_edit()
        command.run(edit)
        self.view.end_edit(edit)


def run():
    """Run all tests from this module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2).run(suite)
