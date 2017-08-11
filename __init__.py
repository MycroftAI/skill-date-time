# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from mycroft.version import CORE_VERSION_MAJOR, \
     CORE_VERSION_MINOR, CORE_VERSION_BUILD
import datetime
from os.path import abspath
import tzlocal
from adapt.intent import IntentBuilder
from astral import Astral
from pytz import timezone
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import time
from threading import Timer
from tzwhere import tzwhere
from geopy.geocoders import Nominatim

__author__ = 'ryanleesipes', 'jdorleans', 'connorpenrod', 'michaelnguyen', \
             'jarbas'

LOGGER = getLogger(__name__)

compatible_core_version_sum = 27

sum_of_core = CORE_VERSION_MAJOR + CORE_VERSION_MINOR + CORE_VERSION_BUILD
if sum_of_core >= compatible_core_version_sum:
    import mycroft.client.enclosure.display_manager as DisplayManager


# TODO - Localization
# TODO - Use scheduled_skills.py and settings.py in Skill dir to implment timer
class TimeSkill(MycroftSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.astral = Astral()
        self.message = None
        self.isClockRunning = False
        self.timer = Timer(5, self._update_time)

    @property
    def format(self):
        if self.config_core.get('time_format') == 'full':
            return "%H:%M"
        else:
            return "%I:%M, %p"

    def initialize(self):
        self.__build_time_intent()
        self.__build_display_intent()

    def __build_time_intent(self):
        intent = IntentBuilder("TimeIntent").require("QueryKeyword") \
            .require("TimeKeyword").optionally("Location").build()
        self.register_intent(intent, self.handle_time_intent)

    def __build_display_intent(self):
        intent = IntentBuilder("DisplayIntent").require("DisplayKeyword") \
            .require("TimeKeyword").optionally("Location").build()
        self.register_intent(intent, self.handle_display_intent)

    def get_timezone(self, locale):
        try:
            # This handles common city names, like "Dallas" or "Paris"
            return timezone(self.astral[locale].timezone)
        except:
            try:
                # This handles codes like "America/Los_Angeles"
                return timezone(locale)
            except:
                try:
                    # get timezone from coordinates of OpenStreetMap Nominatim
                    #  for this location
                    geolocator = Nominatim()
                    location = geolocator.geocode(locale)
                    lat = float(location.latitude)
                    lon = float(location.longitude)
                    tz = tzwhere.tzwhere().tzNameAt(lat, lon)
                    return timezone(tz)
                except Exception as e:
                    return None

    def get_time(self):
        location = self.message.data.get("Location")  # optional parameter
        nowUTC = datetime.datetime.now(timezone('UTC'))
        tz = self.get_timezone(self.location_timezone)

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return

            # Convert UTC to appropriate timezone and format
        return nowUTC.astimezone(tz).strftime(self.format)

    def display(self, current_time):
        # Map time to display code for Mark1 faceplate

        code_dict = {
            ':': 'CIICAA',
            '0': 'EIMHEEMHAA',
            '1': 'EIIEMHAEAA',
            '2': 'EIEHEFMFAA',
            '3': 'EIEFEFMHAA',
            '4': 'EIMBABMHAA',
            '5': 'EIMFEFEHAA',
            '6': 'EIMHEFEHAA',
            '7': 'EIEAEAMHAA',
            '8': 'EIMHEFMHAA',
            '9': 'EIMBEBMHAA',
        }
        if current_time is None:
            return
        value_list = [val for val in current_time]
        code_list = []

        for val in value_list[:5]:
            code_list.append(code_dict[val])

        # # clear screen

        self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                     refresh=False)
        self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                     x=24, refresh=False)

        xoffset = 7
        for code in code_list:
            self.enclosure.mouth_display(code, x=xoffset, y=0,
                                         refresh=False)
            if code == 'CIICAA':
                xoffset += 2
            else:
                xoffset += 4

    def _should_display_time(self):
        _get_active = DisplayManager.get_active
        if _get_active() == "" or _get_active() == "TimeSkill":
            return True
        else:
            return False

    def _update_time(self):
        if self.isClockRunning:
            current_time = self.get_time()
            if self.timer.is_alive():
                self.timer.cancel()
                self.timer = Timer(5, self._update_time)
            if self._should_display_time():
                self.display(current_time)
            self.timer.start()

    def handle_time_intent(self, message):
        self.message = message  # optional parameter
        self.isClockRunning = True
        ti = self.get_time()
        if ti is None:
            return
        self.speak_dialog("time.current", {"time": ti})
        if sum_of_core >= compatible_core_version_sum:
            self._update_time()

    def handle_display_intent(self, message):
        self.message = message
        self.isClockRunning = True
        if sum_of_core >= compatible_core_version_sum:
            self._update_time()

    def stop(self):
        self.timer.cancel()
        self.timer = Timer(5, self._update_time)
        self.enclosure.reset()
        self.isClockRunning = False


def create_skill():
    return TimeSkill()
