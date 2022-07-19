# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending
import datetime
import shutil
import unittest
import pytest
import datetime as dt

from os import mkdir
from os.path import dirname, join, exists
from pytz import timezone
from mock import Mock
from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus


class TestSkill(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from mycroft.skills.skill_loader import SkillLoader

        bus = FakeBus()
        bus.run_in_thread()
        skill_loader = SkillLoader(bus, dirname(dirname(__file__)))
        skill_loader.load()
        cls.skill = skill_loader.instance
        cls.test_fs = join(dirname(__file__), "skill_fs")
        if not exists(cls.test_fs):
            mkdir(cls.test_fs)
        cls.skill.settings_write_path = cls.test_fs
        cls.skill.file_system.path = cls.test_fs

        # Override speak and speak_dialog to test passed arguments
        cls.skill.speak = Mock()
        cls.skill.speak_dialog = Mock()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.test_fs)

    def tearDown(self) -> None:
        self.skill.speak.reset_mock()
        self.skill.speak_dialog.reset_mock()

    def test_00_skill_init(self):
        # Test any parameters expected to be set in init or initialize methods
        from neon_utils.skills import NeonSkill

        self.assertIsInstance(self.skill, NeonSkill)

    def test_handle_idle(self):
        class MockGui:
            def __init__(self):
                self._data = dict()
                self.show_page = Mock()

            def __setitem__(self, key, value):
                self._data[key] = value

            def __getitem__(self, item):
                return self._data[item]

            @staticmethod
            def clear():
                pass

        real_gui = self.skill.gui
        mock_gui = MockGui()
        self.skill.gui = mock_gui

        self.skill.handle_idle(Message("test"))
        self.assertIsInstance(mock_gui["time_string"], str)
        self.assertEqual(mock_gui["ampm_string"], '')
        self.assertIsInstance(mock_gui["date_string"], str)
        self.assertIsInstance(mock_gui["weekday_string"], str)
        self.assertIsInstance(mock_gui["month_string"], str)
        self.assertIsInstance(mock_gui["year_string"], str)
        self.skill.gui.show_page.assert_called_once()
        self.skill.gui.show_page.assert_called_with("idle.qml")

        self.skill.gui = real_gui

    def test_get_display_date(self):
        from neon_utils.user_utils import get_default_user_config
        config = get_default_user_config()
        config['user']['username'] = 'test_user'
        config['units']['date'] = "MDY"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})

        test_date = dt.datetime(month=1, day=2, year=2000)

        date_str = self.skill.get_display_date(test_date, message=test_message)
        self.assertEqual(date_str, "1/2/2000")

        config['units']['date'] = "DMY"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        date_str = self.skill.get_display_date(test_date, message=test_message)
        self.assertEqual(date_str, "2/1/2000")

        config['units']['date'] = "YMD"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        date_str = self.skill.get_display_date(test_date, message=test_message)
        self.assertEqual(date_str, "2000/1/2")

        now_date_str = self.skill.get_display_date()
        self.assertNotEqual(date_str, now_date_str)

    def test_get_display_current_time(self):
        from neon_utils.user_utils import get_default_user_config
        config = get_default_user_config()
        config['user']['username'] = 'test_user'


        current_time = self.skill.get_display_current_time()
        self.assertIsInstance(current_time, str)
        self.assertEqual(len(current_time.split(':')), 2)

        current_time_honolulu = self.skill.get_display_current_time("honolulu")
        self.assertIsInstance(current_time_honolulu, str)
        self.assertEqual(len(current_time.split(':')), 2)
        self.assertNotEqual(current_time, current_time_honolulu)

        config['units']['time'] = 24
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})

        dt_utc = dt.datetime.now(dt.timezone.utc).replace(hour=23, minute=30)
        utc_time = self.skill.get_display_current_time(dt_utc=dt_utc,
                                                       message=test_message)
        self.assertEqual(utc_time, "23:30")
        az_time = self.skill.get_display_current_time("phoenix", dt_utc,
                                                      message=test_message)
        self.assertEqual(az_time, "16:30")

        self.skill.settings['use_ampm'] = True
        config['units']['time'] = 12
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        utc_time = self.skill.get_display_current_time(dt_utc=dt_utc,
                                                       message=test_message)
        self.assertEqual(utc_time, "11:30 PM")
        az_time = self.skill.get_display_current_time("phoenix", dt_utc,
                                                      message=test_message)
        self.assertEqual(az_time, "4:30 PM")

        self.skill.settings['use_ampm'] = False
        utc_time = self.skill.get_display_current_time(dt_utc=dt_utc,
                                                       message=test_message)
        self.assertEqual(utc_time, "11:30")
        az_time = self.skill.get_display_current_time("phoenix", dt_utc,
                                                      message=test_message)
        self.assertEqual(az_time, "4:30")

    def test_get_weekday(self):
        self.assertIsInstance(self.skill.get_weekday(), str)
        today = dt.datetime.now(dt.timezone.utc)
        tomorrow = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)
        self.assertNotEqual(self.skill.get_weekday(today),
                            self.skill.get_weekday(tomorrow))
        self.assertNotEqual(self.skill.get_weekday(location="Perth"),
                            self.skill.get_weekday(location="Honolulu"))

        known_day = dt.datetime(day=1, month=1, year=2000)
        self.assertEqual(self.skill.get_weekday(known_day), "Saturday")

    def test_get_month_date(self):
        from neon_utils.user_utils import get_default_user_config
        config = get_default_user_config()
        config['user']['username'] = 'test_user'
        test_date = dt.datetime(month=1, day=1, year=2000)

        config['units']['date'] = "MDY"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        date_str = self.skill.get_month_date(test_date, message=test_message)
        self.assertEqual(date_str, "January 01")

        config['units']['date'] = "DMY"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        date_str = self.skill.get_month_date(test_date, message=test_message)
        self.assertEqual(date_str, "01 January")

        config['units']['date'] = "YMD"
        test_message = Message("test", {}, {"username": "test_user",
                                            "user_profiles": [config]})
        date_str = self.skill.get_month_date(test_date, message=test_message)
        self.assertEqual(date_str, "January 01")

        now_date_str = self.skill.get_month_date()
        self.assertNotEqual(date_str, now_date_str)

    def test_get_year(self):
        self.assertIsInstance(self.skill.get_year(), str)
        date = datetime.datetime(month=1, day=1, year=2000)
        self.assertEqual(self.skill.get_year(date), "2000")
        self.assertEqual(self.skill.get_year(date, "Seattle"), "2000")
        self.assertIsInstance(self.skill.get_year(location="Seattle"), str)

    def test_get_next_leap_year(self):
        for year in (2000, 2001, 2002, 2003):
            self.assertEqual(self.skill.get_next_leap_year(year), 2004)
        self.assertEqual(self.skill.get_next_leap_year(2004), 2008)

    def test_is_leap_year(self):
        for year in (1999, 2001, 2002, 2003):
            self.assertFalse(self.skill.is_leap_year(year))
        for year in (2000, 2004, 2008):
            self.assertTrue(self.skill.is_leap_year(year))

    def test_handle_query_time(self):
        default_location_message = Message("test_message",
                                           {"Query": "what",
                                            "Time": "time",
                                            "utterance": "what time is it"})
        self.skill.handle_query_time(default_location_message)
        self.skill.speak_dialog.assert_called_once()
        call_args = self.skill.speak_dialog.call_args[0]
        self.assertEqual(call_args[0], "time.current")
        self.assertEqual(set(call_args[1].keys()), {"time"})

        spec_location_message = Message("test_message",
                                        {"Query": "what",
                                         "Time": "time",
                                         "Location": "london",
                                         "utterance": "what time is it in london"})
        self.skill.handle_query_time(spec_location_message)
        call_args = self.skill.speak_dialog.call_args[0]
        self.assertEqual(call_args[0], "TimeInLocation")
        self.assertEqual(call_args[1]["location"], "London")
        self.assertEqual(set(call_args[1].keys()), {"location", "time"})

    def test_handle_query_date(self):
        default_location_message = Message("test_message",
                                           {"Query": "what",
                                            "Date": "date",
                                            "utterance": "what is the date"})
        self.skill.handle_query_date(default_location_message)
        self.skill.speak_dialog.assert_called_once()
        call_args = self.skill.speak_dialog.call_args[0]
        self.assertEqual(call_args[0], "date")
        self.assertEqual(set(call_args[1].keys()), {"date"})

    def test_get_timezone(self):
        la_timezone = timezone("America/Los_Angeles")
        dict_test_cases = [
            {"city": "seattle"},
            {"city": "seattle", "state": "washington"},
            {"city": "seattle", "country": "united states"},
            # "pacific time",
            "los angeles time"
        ]
        for case in dict_test_cases:
            tz = self.skill.get_timezone(case)
            self.assertIsInstance(tz, dt.tzinfo)
            self.assertEqual(tz, la_timezone)
        str_test_cases = {
            "seattle": la_timezone,
            "seattle washington": la_timezone,
            "seattle, wa": la_timezone,
            "paris texas": timezone("America/Chicago")
        }
        for case in str_test_cases:
            self.assertEqual(self.skill.get_timezone(case), str_test_cases[case])

    def test_get_local_datetime(self):
        # TODO
        pass

    def test_get_spoken_time(self):
        # TODO
        pass

    def test_show_time_gui(self):
        # TODO
        pass

    def test_show_date_gui(self):
        # TODO
        pass

    def test_extract_location(self):
        # TODO
        pass

    def test_get_timezone_from_neon_utils(self):
        self.assertEqual(self.skill._get_timezone_from_neon_utils("seattle"),
                         timezone("America/Los_Angeles"))

    def test_get_timezone_from_builtins(self):
        self.assertEqual(self.skill._get_timezone_from_builtins("seattle"),
                         timezone("America/Los_Angeles"))

    def test_get_timezone_from_table(self):
        self.assertEqual(self.skill._get_timezone_from_table("pacific time"),
                         timezone("America/Los_Angeles"))
        self.assertEqual(self.skill._get_timezone_from_table("eastern time"),
                         timezone("America/New_York"))
        self.assertEqual(self.skill._get_timezone_from_table("china"),
                         timezone("Asia/Hong_Kong"))
        self.assertEqual(self.skill._get_timezone_from_table("paris texas"),
                         timezone("America/Chicago"))

    def test_get_timezone_from_fuzzymatch(self):
        self.assertEqual(self.skill._get_timezone_from_fuzzymatch("los angeles"),
                         timezone("America/Los_Angeles"))


if __name__ == '__main__':
    pytest.main()
