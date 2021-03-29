# Copyright 2021 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import pytest
import unittest

from ..date import get_next_leap_year, is_leap_year


class TestLeapYears(unittest.TestCase):
    def test_get_next_leap_year(self):
        self.assertEqual(get_next_leap_year(2020), 2024)
        self.assertEqual(get_next_leap_year(2021), 2024)
        self.assertEqual(get_next_leap_year(2024), 2028)

    def test_is_leap_year(self):
        self.assertTrue(is_leap_year(2020))
        self.assertTrue(is_leap_year(2024))
        self.assertTrue(is_leap_year(2000))
        self.assertFalse(is_leap_year(2021))
        self.assertFalse(is_leap_year(2022))
        self.assertFalse(is_leap_year(2100))