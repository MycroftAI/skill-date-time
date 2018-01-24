# Copyright 2017, Mycroft AI Inc.
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

import datetime
import tzlocal
from astral import Astral
from pytz import timezone
import time

from adapt.intent import IntentBuilder
import mycroft.audio
from mycroft.skills.core import MycroftSkill, intent_handler
import mycroft.client.enclosure.display_manager as DisplayManager


# TODO: Move to mycroft.util.format.py
def nice_time(dt, lang="en-us", speech=True, use_24hour=False,
              use_ampm=False):
    '''
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        lang (str): code for the language to use
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    '''

    if use_24hour:
        # e.g. "03:01" or "14:22"
        str = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            str = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            str = dt.strftime("%I:%M")
        if str[0] == '0':
            str = str[1:]  # strip leading zeros
        return str

    if not speech:
        return str

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8 hundred" or "13 hundred"
        if str[0] == '0':
            if str[1] == '0':
                speak = "0 0"
            else:
                speak = "0 " + str[1]
        else:
            speak += str[0:2]

        if str[3] == '0':
            if str[4] == '0':
                # Ignore the 00 in, for example, 13:00
                speak += " hundred"  # TODO: Localize
            else:
                speak += " o " + str[4]  # TODO: Localize
        else:
            if str[0] == '0':
                speak += " " + str[3:5]
            else:
                # TODO: convert "23" to "twenty three" in helper method

                # Mimic is speaking "23 34" as "two three 43" :(
                # but it does say "2343" correctly.  Not ideal for general
                # TTS but works for the moment.
                speak += ":" + str[3:5]

        return speak
    else:
        if lang.startswith("en"):
            if dt.hour == 0 and dt.minute == 0:
                return "midnight"  # TODO: localize
            if dt.hour == 12 and dt.minute == 0:
                return "noon"  # TODO: localize
            # TODO: "half past 3", "a quarter of 4" and other idiomatic times

            # lazy for now, let TTS handle speaking "03:22 PM" and such
        return str


class TimeSkill(MycroftSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.astral = Astral()
        self.displayed_time = None
        self.display_tz = None
        self.active = False

    def initialize(self):
        # Start a callback that repeats every 10 seconds
        now = datetime.datetime.now()
        callback_time = (datetime.datetime(now.year, now.month, now.day,
                                           now.hour, now.minute) +
                         datetime.timedelta(seconds=60))
        self.schedule_repeating_event(self.update_display, callback_time, 10)

    @property
    def use_24hour(self):
        return self.config_core.get('time_format') == 'full'

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

    def get_local_datetime(self, location):
        nowUTC = datetime.datetime.now(timezone('UTC'))

        if self.display_tz:
            tz = self.display_tz
        else:
            tz = self.get_timezone(self.location_timezone)

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return None

        return nowUTC.astimezone(tz)

    def get_display_time(self, location=None):
        # Get a formatted digital clock time based on the user preferences
        dt = self.get_local_datetime(location)
        if not dt:
            return

        return nice_time(dt, self.lang, speech=False,
                         use_24hour=self.use_24hour)

    def get_spoken_time(self, location=None):
        # Get a formatted spoken time based on the user preferences
        dt = self.get_local_datetime(location)
        if not dt:
            return

        return nice_time(dt, self.lang, speech=True,
                         use_24hour=self.use_24hour)

    def display(self, display_time):
        # Map characters to the display encoding for a Mark 1
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

        # clear screen (draw two blank halves)
        self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                     refresh=False)
        self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                     x=24, refresh=False)

        # draw the time, centered on display
        xoffset = (32 - (4*(len(display_time))-2)) / 2
        self.log.debug("Offset: "+str(display_time))
        for c in display_time:
            if c in code_dict:
                self.enclosure.mouth_display(img_code=code_dict[c],
                                             x=xoffset, refresh=False)
                if c == ":":
                    xoffset += 2  # colon is 1 pixels + a space
                else:
                    xoffset += 4  # digits are 3 pixels + a space

    def _should_display_time(self):
        # check if the display is being used by another skill right now
        _get_active = DisplayManager.get_active
        return _get_active() == "" or _get_active() == "TimeSkill"

    def update_display(self, force=False):
        if self.active:
            return

        if self.settings["show_time"].lower() == "true":
            if force or self._should_display_time():
                # user requested display of time
                current_time = self.get_display_time()
                if self.displayed_time != current_time:
                    self.displayed_time = current_time
                    self.display(current_time)
            else:
                self.displayed_time = None  # another skill is using display
        else:
            # clear the display
            if self.displayed_time:
                self.enclosure.mouth_reset()
                self.displayed_time = None
            return

    @intent_handler(IntentBuilder("").require("Query").require("Time").
                    optionally("Location"))
    def handle_query_time(self, message):
        location = message.data.get("Location")
        current_time = self.get_spoken_time(location)
        if not current_time:
            return

        # speak it
        self.speak_dialog("time.current", {"time": current_time})

        # and briefly show the time
        self.active = True
        self.enclosure.deactivate_mouth_events()
        self.display(self.get_display_time(location))
        time.sleep(5)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.active = False
        self.displayed_time = None

    @intent_handler(IntentBuilder("").require("Display").require("Time").
                    optionally("Location"))
    def handle_show_time(self, message):
        self.display_tz = None
        location = message.data.get("Location")
        if location:
            tz = self.get_timezone(location)
            if not tz:
                self.speak_dialog("time.tz.not.found", {"location": location})
                return
            else:
                self.display_tz = tz

        # show time immediately
        self.settings["show_time"] = "true"
        self.update_display(True)

    @intent_handler(IntentBuilder("").require("Query").require("Date").
                    optionally("Location"))
    def handle_query_date(self, message):
        local_date = self.get_local_datetime(message.data.get("Location"))
        if not local_date:
            return

        # Get the current date
        speak = local_date.strftime("%A, %B %-d, %Y")
        if self.config_core.get('date_format') == 'MDY':
            show = local_date.strftime("%-m/%-d/%Y")
        else:
            show = local_date.strftime("%Y/%-d/%-m")

        # speak it
        self.speak_dialog("date", {"date": speak})

        # and briefly show the time
        self.active = True
        self.enclosure.deactivate_mouth_events()
        self.enclosure.mouth_text(show)
        time.sleep(10)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.active = False
        self.displayed_time = None


def create_skill():
    return TimeSkill()
