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
import re
import pytz
import time
import tzlocal
from astral import Astral
import holidays

from adapt.intent import IntentBuilder
import mycroft.audio
# from mycroft.util.format import nice_time
from mycroft.util.format import pronounce_number, nice_date
from mycroft.util.lang.format_de import nice_time_de, pronounce_ordinal_de
from mycroft.messagebus.message import Message
from mycroft import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.parse import extract_datetime, fuzzy_match, extract_number
from mycroft.util.time import now_utc, default_timezone

# TODO:
#   * what time is it in Sydney
#   * what day is it in Sydney
#   * what day is july 4th
#   * what day is Christmas 2020

# TODO: This is temporary until nice_time() gets fixed in mycroft-core's
# next release
def nice_time(dt, lang, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        lang (string): ignored
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """

    # If language is German, use nice_time_de
    if lang.lower().startswith("de"):
        return nice_time_de(dt, speech, use_24hour, use_ampm)

    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8 hundred" or "13 hundred"
        if string[0] == '0':
            speak += pronounce_number(int(string[0]), lang) + " "
            speak += pronounce_number(int(string[1]), lang)
        else:
            speak = pronounce_number(int(string[0:2]), lang)

        speak += " "
        if string[3:5] == '00':
            speak += "hundred"
        else:
            if string[3] == '0':
                speak += pronounce_number(0) + " "
                speak += pronounce_number(int(string[4]), lang)
            else:
                speak += pronounce_number(int(string[3:5]), lang)
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "midnight"
        if dt.hour == 12 and dt.minute == 0:
            return "noon"
        # TODO: "half past 3", "a quarter of 4" and other idiomatic times

        if dt.hour == 0:
            speak = pronounce_number(12, lang)
        elif dt.hour < 13:
            speak = pronounce_number(dt.hour, lang)
        else:
            speak = pronounce_number(dt.hour - 12, lang)

        if dt.minute == 0:
            if not use_ampm:
                return speak + " o'clock"
        else:
            if dt.minute < 10:
                speak += " oh"
            speak += " " + pronounce_number(dt.minute, lang)

        if use_ampm:
            if dt.hour > 11:
                speak += " PM"
            else:
                speak += " AM"

        return speak

def nice_date_de(local_date):
    # dates are returned as, for example:
    # "Samstag, der siebte Juli zweitausendachtzehn"
    # this returns the years as regular numbers,
    # not 19 hundred ..., but one thousand nine hundred
    # which is fine from the year 2000

    de_months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                 'Juli', 'August', 'September', 'October', 'November',
                 'Dezember']

    de_weekdays = ['Montag', 'Dienstag', 'Mittwoch',
                   'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    return de_weekdays[local_date.weekday()] + ", der " \
            + pronounce_ordinal_de(local_date.day) + " " \
            + de_months[local_date.month - 1] \
            + " " + pronounce_number(local_date.year, lang = "de")

class TimeSkill(MycroftSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.astral = Astral()
        self.displayed_time = None
        self.display_tz = None
        self.answering_query = False

    def initialize(self):
        # Start a callback that repeats every 10 seconds
        # TODO: Add mechanism to only start timer when UI setting
        #       is checked, but this requires a notifier for settings
        #       updates from the web.
        now = datetime.datetime.now()
        callback_time = (datetime.datetime(now.year, now.month, now.day,
                                           now.hour, now.minute) +
                         datetime.timedelta(seconds=60))
        self.schedule_repeating_event(self.update_display, callback_time, 10)

    @property
    def use_24hour(self):
        return self.config_core.get('time_format') == 'full'

    def get_timezone(self, locale):
        self.log.debug("GET_TIMEZONE: "+str(locale))
        try:
            # This handles common city names, like "Dallas" or "Paris"
            return pytz.timezone(self.astral[locale].timezone)
        except:
            pass

        try:
            # This handles codes like "America/Los_Angeles"
            return pytz.timezone(locale)
        except:
            pass

        # Check lookup table for other timezones.  This can also
        # be a translation layer.
        # E.g. "china = GMT+8"
        timezones = self.translate_namedvalues("timezone.value")
        for timezone in timezones:
            if locale.lower() == timezone.lower():
                # assumes translation is correct
                return pytz.timezone(timezones[timezone].strip())

        # Now we gotta get a little fuzzy
        # Look at the pytz list of all timezones. It consists of
        # Location/Name pairs.  For example:
        # ["Africa/Abidjan", "Africa/Accra", ... "America/Denver", ...
        #  "America/New_York", ..., "America/North_Dakota/Center", ...
        #  "Cuba", ..., "EST", ..., "Egypt", ..., "Etc/GMT+3", ...
        #  "Etc/Zulu", ... "US/Eastern", ... "UTC", ..., "Zulu"]
        target = locale.lower()
        best = None
        for name in pytz.all_timezones:
            normalized = name.lower().replace("_", " ").split("/")
            if len(normalized) == 1:
                pct = fuzzy_match(normalized[0], target)
            elif len(normalized) == 2:
                pct = fuzzy_match(normalized[1], target)
                # TODO: if pct <
            if not best or pct >= best[0]:
                best = (pct, name)
        if best and best[0] > 0.8:
           # solid choice
           return pytz.timezone(best[1])
        if best and best[0] > 0.3:
            if self.ask_yesno("did you mean "+ best[1]) == "yes":
                return pytz.timezone(best[1])

        return None

    def get_local_datetime(self, location, dtUTC=None):
        if not dtUTC:
            dtUTC = now_utc()
        if self.display_tz:
            # User requested times be shown in some timezone
            tz = self.display_tz
        else:
            # Use default timezone
            tz = default_timezone()

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return None

        return dtUTC.astimezone(tz)

    def get_display_current_time(self, location=None):
        # Get a formatted digital clock time based on the user preferences
        dt = self.get_local_datetime(location)
        if not dt:
            return

        return nice_time(dt, self.lang, speech=False,
                         use_24hour=self.use_24hour)

    def get_spoken_current_time(self, location=None):
        # Get a formatted spoken time based on the user preferences
        dt = self.get_local_datetime(location)
        if not dt:
            return

        say_am_pm = bool(location)  # speak AM/PM when talking about somewhere else
        s = nice_time(dt, self.lang, speech=True,
                      use_24hour=self.use_24hour, use_ampm=say_am_pm)
        # HACK: Mimic 2 has a bug with saying "AM".  Work around it for now.
        if say_am_pm:
            s = s.replace("AM", "A.M.")
        return s

    def display(self, display_time):
        if not display_time:
            return

        # Map characters to the display encoding for a Mark 1
        # (4x8 except colon, which is 2x8)
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

        # clear screen (draw two blank sections, numbers cover rest)
        if len(display_time) == 4:
            # for 4-character times, 9x8 blank
            self.enclosure.mouth_display(img_code="JIAAAAAAAAAAAAAAAAAA",
                                         refresh=False)
            self.enclosure.mouth_display(img_code="JIAAAAAAAAAAAAAAAAAA",
                                         x=22, refresh=False)
        else:
            # for 5-character times, 7x8 blank
            self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                         refresh=False)
            self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                         x=24, refresh=False)

        # draw the time, centered on display
        xoffset = (32 - (4*(len(display_time))-2)) / 2
        for c in display_time:
            if c in code_dict:
                self.enclosure.mouth_display(img_code=code_dict[c],
                                             x=xoffset, refresh=False)
                if c == ":":
                    xoffset += 2  # colon is 1 pixels + a space
                else:
                    xoffset += 4  # digits are 3 pixels + a space

        if self._is_alarm_set():
            # Show a dot in the upper-left
            self.enclosure.mouth_display(img_code="CIAACA", x=1, refresh=False)
        else:
            self.enclosure.mouth_display(img_code="CIAAAA", x=1, refresh=False)

    def _is_alarm_set(self):
        msg = self.bus.wait_for_response(Message("private.mycroftai.has_alarm"))
        return msg and msg.data.get("active_alarms", 0) > 0

    def _is_display_idle(self):
        # check if the display is being used by another skill right now
        # or _get_active() == "TimeSkill"
        return self.enclosure.display_manager.get_active() == ''

    def update_display(self, force=False):
        # Don't show idle time when answering a query to prevent
        # overwriting the displayed value.
        if self.answering_query:
            return

        if self.settings.get("show_time", False):
            # user requested display of time while idle
            if (force is True) or self._is_display_idle():
                current_time = self.get_display_current_time()
                if self.displayed_time != current_time:
                    self.displayed_time = current_time
                    self.display(current_time)
                    # return mouth to 'idle'
                    self.enclosure.display_manager.remove_active()
            else:
                self.displayed_time = None  # another skill is using display
        else:
            # time display is not wanted
            if self.displayed_time:
                if self._is_display_idle():
                    # erase the existing displayed time
                    self.enclosure.mouth_reset()
                    # return mouth to 'idle'
                    self.enclosure.display_manager.remove_active()
                self.displayed_time = None

    @intent_file_handler("what.time.is.it.intent")
    def handle_query_time_alt(self, message):
        self.log.info("FORWARDING PADATIOUS INTENT MATCH ")
        self.handle_query_time(message)

    def _extract_location(self, message):
        # if "Location" in message.data:
        #     return message.data["Location"]

        utt = message.data.get('utterance') or ""
        rx_file = self.find_resource('location.rx', 'regex')
        if rx_file:
            with open(rx_file) as f:
                for pat in f.read().splitlines():
                    pat = pat.strip()
                    if pat and pat[0] == "#":
                        continue
                    res = re.search(pat, utt)
                    if res:
                        try:
                            return res.group("Location")
                        except IndexError:
                            pass
        return None

    @intent_handler(IntentBuilder("").require("Query").require("Time").
                    optionally("Location"))
    def handle_query_time(self, message):
        location = self._extract_location(message)
        self.log.info("LOCATION: "+str(location))
        current_time = self.get_spoken_current_time(location)
        if not current_time:
            return

        # speak it
        self.speak_dialog("time.current", {"time": current_time})

        # and briefly show the time
        self.answering_query = True
        self.enclosure.deactivate_mouth_events()
        self.display(self.get_display_current_time(location))
        time.sleep(5)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.answering_query = False
        self.displayed_time = None

    @intent_handler(IntentBuilder("").require("Display").require("Time").
                    optionally("Location"))
    def handle_show_time(self, message):
        self.display_tz = None
        location = self._get_location(message)
        self.log.info("Location: "+str(location))
        if location:
            tz = self.get_timezone(location)
            if not tz:
                self.speak_dialog("time.tz.not.found", {"location": location})
                return
            else:
                self.display_tz = tz
        else:
            self.display_tz = None

        # show time immediately
        self.settings["show_time"] = True
        self.update_display(True)

    @intent_handler(IntentBuilder("").require("Query").require("Date").
                    optionally("Location"))
    def handle_query_date(self, message):
        utt = message.data.get('utterance').lower() or ""
        extract = extract_datetime(utt)

        day = extract[0]
        # check if a Holiday was requested
        year = extract_number(utt)
        if not year or year < 1500 or year > 3000:  # filter out non-years
            year = day.year
        all = {}
        # TODO: How to pick a location for holidays?
        for st in holidays.US.STATES:
            l = holidays.US(years=[year], state=st)
            for d, name in l.items():
                if not name in all:
                    all[name] = d
        for name in all:
            d = all[name]
            # self.log.info("Day, name: " +str(d) + " " + str(name))
            if name.replace(" Day", "").lower() in utt:
                day = d
                break

        location = self._extract_location(message)
        if location:
            # TODO: Timezone math!
            day = self.get_local_datetime(location, dtUTC=day)

        self.log.info("Day:  "+str(day))
        if self.lang.lower().startswith("de"):
            speak = nice_date_de(day)
        else:
            speak = nice_date(day)

        if self.config_core.get('date_format') == 'MDY':
            show = day.strftime("%-m/%-d/%Y")
        else:
            show = day.strftime("%Y/%-d/%-m")

        # speak it
        self.speak_dialog("date", {"date": speak})

        # and briefly show the time
        self.answering_query = True
        self.enclosure.deactivate_mouth_events()
        self.enclosure.mouth_text(show)
        time.sleep(10)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.answering_query = False
        self.displayed_time = None


def create_skill():
    return TimeSkill()
