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

from ..format import speakable_timezone


class TestSpeakableTimezone(unittest.TestCase):
    def test_speakable_timezone(self):
        self.assertEqual(speakable_timezone("North_Dakota"), "North Dakota")
        self.assertEqual(speakable_timezone("EasterIsland"), "Easter Island")
        self.assertEqual(
            speakable_timezone("America/Los_Angeles"), "Los Angeles America"
        )
        self.assertEqual(
            speakable_timezone("America/North Dakota/Center"),
            "Center North Dakota America",
        )
