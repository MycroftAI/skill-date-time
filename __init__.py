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


import datetime
from os.path import abspath
import tzlocal
from adapt.intent import IntentBuilder
from astral import Astral
from pytz import timezone
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import time

__author__ = 'ryanleesipes', 'jdorleans'

LOGGER = getLogger(__name__)


# TODO - Localization
class TimeSkill(MycroftSkill):
    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.astral = Astral()
        self.init_format()

    def init_format(self):
        if self.config_core.get('time_format') == 'full':
            self.format = "%H:%M"
        else:
            self.format = "%I:%M, %p"

    def initialize(self):
        self.__build_speak_intent()
        self.__build_display_intent()

    def __build_speak_intent(self):
        intent = IntentBuilder("SpeakIntent").require("QueryKeyword") \
            .require("TimeKeyword").optionally("Location").build()
        self.register_intent(intent, self.handle_speak_intent)

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
                return None

    def display(self, current_time):
        # Map time to display code for Mark1 faceplate
        code_dict = {
            ':': 'BIEB',
            '0': 'DIODCCOD',
            '1': 'DIECODAC',
            '2': 'DIKDKCOC',
            '3': 'DIKCKCOD',
            '4': 'DIOAIAOD',
            '5': 'DIOCKCKD',
            '6': 'DIODKCKD',
            '7': 'DICACAOD',
            '8': 'DIODKCOD',
            '9': 'DIOAKAOD',
        }

        value_list = [val for val in current_time]
        code_list = []

        for val in value_list[:5]:
            code_list.append(code_dict[val])

        # clear screen
        self.enclosure.reset()

        # x is used to offset the images
        xoffset = 7
        for code in code_list:
            self.enclosure.mouth_display(code, x=xoffset, y=1,
                                         refresh=False)
            if code == 'BIEB':
                xoffset += 2
            else:
                xoffset += 4

    def handle_speak_intent(self, message):
        location = message.data.get("Location")  # optional parameter
        nowUTC = datetime.datetime.now(timezone('UTC'))
        tz = self.get_timezone(self.location_timezone)

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return

        # Convert UTC to appropriate timezone and format
        current_time = nowUTC.astimezone(tz).strftime(self.format)
        self.display(current_time)
        self.enclosure.deactivate_mouth_events()
        self.speak_dialog("time.current", {"time": current_time})

        time.sleep(4)
        self.enclosure.activate_mouth_events()
        self.enclosure.reset()

    def handle_display_intent(self, message):
        location = message.data.get("Location")  # optional parameter
        nowUTC = datetime.datetime.now(timezone('UTC'))
        tz = self.get_timezone(self.location_timezone)

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return

        # Convert UTC to appropriate timezone and format
        current_time = nowUTC.astimezone(tz).strftime(self.format)
        self.display(current_time)

    def stop(self):
        pass


def create_skill():
    return TimeSkill()
