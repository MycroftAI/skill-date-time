# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
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

import re
import geocoder
import pytz

from datetime import tzinfo, datetime
from typing import Union, Optional

from lingua_franca import load_language
from mycroft import intent_file_handler
from timezonefinder import TimezoneFinder
from mycroft_bus_client import Message
from ovos_utils.parse import fuzzy_match
from neon_utils.location_utils import get_coordinates, get_timezone
from adapt.intent import IntentBuilder
from neon_utils.skills.neon_skill import NeonSkill, LOG
from neon_utils.message_utils import dig_for_message, request_for_neon
from neon_utils.user_utils import get_user_prefs

from mycroft.skills.core import intent_handler, resting_screen_handler,\
    skill_api_method
from mycroft.util.format import nice_time, date_time_format


def speakable_timezone(tz: str) -> str:
    """Convert timezone to a better speakable version

    Splits joined words,  e.g. EasterIsland  to "Easter Island",
    "North_Dakota" to "North Dakota" etc.
    Then parses the output into the correct order for speech,
    eg. "America/North Dakota/Center" to
    resulting in something like  "Center North Dakota America", or
    "Easter Island Chile"
    """
    say = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", tz)
    say = say.replace("_", " ")
    say = say.split("/")
    say.reverse()
    return " ".join(say)


class TimeSkill(NeonSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")

    @property
    def use_24hour(self) -> bool:
        return get_user_prefs()["units"]["time"] == 24

    @resting_screen_handler('Time and Date')
    def handle_idle(self, _):
        """
        Handler for displaying GUI resting screen
        """
        self.gui.clear()
        self.log.debug('Activating Time/Date resting page')
        self.gui['time_string'] = self.get_display_current_time()
        self.gui['ampm_string'] = ''
        self.gui['date_string'] = self.get_display_date()
        self.gui['weekday_string'] = self.get_weekday()
        self.gui['month_string'] = self.get_month_date()
        self.gui['year_string'] = self.get_year()
        # self.gui['build_date'] = None
        self.gui.show_page('idle.qml')

    @skill_api_method
    def get_display_date(self, day: Optional[datetime] = None,
                         location: Optional[str] = None,
                         message: Message = None) -> str:
        """
        Get the full date for day or location in the configured format.
        :param day: datetime object to display
        :param location: location to get the current datetime of
        :param message: Message containing user profile for request
        :returns: The full date in the user configured format
        """
        message = message or dig_for_message()
        unit_prefs = get_user_prefs(message)['units']
        if not day:
            day = self.get_local_datetime(location, None)
        if unit_prefs.get('date') == 'MDY':
            return day.strftime("%-m/%-d/%Y")
        elif unit_prefs.get('date') == 'YMD':
            return day.strftime("%Y/%-m/%-d")
        elif unit_prefs.get('date') == "DMY":
            return day.strftime("%-d/%-m/%Y")
        else:
            return day.strftime("%Y/%-d/%-m")

    @skill_api_method
    def get_display_current_time(self, location: Optional[str] = None,
                                 dt_utc: Optional[datetime] = None,
                                 message: Message = None) -> \
            Optional[str]:
        """
        Get a formatted digital clock time based on the user preferences
        :param location: location to get the current datetime of
        :param dt_utc: UTC datetime to override current datetime
        :param: Time in the user configured format if location is valid
            else None
        :param message: Message containing user profile for request
        :returns: Formatted string time or None if Exception
        """
        message = message or dig_for_message()
        try:
            dt = self.get_local_datetime(location, message)
            if dt_utc:
                if location:
                    dt = dt_utc.astimezone(dt.tzinfo)
                else:
                    dt = dt_utc
            if not dt:
                return None
            load_language(self.lang)
            # noinspection PyTypeChecker
            return nice_time(dt, self.lang, speech=False,
                             use_24hour=self.use_24hour,
                             use_ampm=self.preference_skill().get('use_ampm',
                                                                  False))
        except Exception as e:
            LOG.error(e)
            return None

    @skill_api_method
    def get_weekday(self, day: Optional[datetime] = None,
                    location: Optional[str] = None) -> str:
        """
        Get the weekday name for a given day.
        :param day: datetime object to get weekday of
        :param location: optional location to get weekday for
        :returns: The name of the weekday (i.e. Monday)
        """
        if not day:
            day = self.get_local_datetime(location, None)
        if self.lang in date_time_format.lang_config.keys():
            localized_day_names = list(
                date_time_format.lang_config[self.lang]['weekday'].values())
            weekday = localized_day_names[day.weekday()]
        else:
            weekday = day.strftime("%A")
        return weekday.capitalize()

    @skill_api_method
    def get_month_date(self, day: Optional[datetime] = None,
                       location: Optional[str] = None,
                       message: Message = None) -> str:
        """
        Get the month and date for a given day and location
        :param day: optional datetime object to get month and date for
        :param location: optional location to get the current datetime of
        :param message: Message containing user profile for request
        :returns: date in the format DD MONTH or MONTH DD
            depending on the users date_format setting.
        """
        message = message or dig_for_message()
        unit_prefs = get_user_prefs(message)["units"]
        if not day:
            day = self.get_local_datetime(location, None)
        if self.lang in date_time_format.lang_config.keys():
            localized_month_names = \
                date_time_format.lang_config[self.lang]['month']
            month = localized_month_names[str(int(day.strftime("%m")))]
        else:
            month = day.strftime("%B")
        month = month.capitalize()
        if "MD" in unit_prefs.get('date'):  # YMD, MDY
            return f"{month} {day.strftime('%d')}"
        else:  # DMY
            return f"{day.strftime('%d')} {month}"

    @skill_api_method
    def get_year(self, day: Optional[datetime] = None,
                 location: Optional[str] = None) -> str:
        """
        Get the year for a given day and location
        :param day: optional datetime object to get year for
        :param location: optional location to get the current year of
        :returns: year in the format YYYY
        """
        if not day:
            day = self.get_local_datetime(location)
        return day.strftime("%Y")

    @skill_api_method
    def get_next_leap_year(self, year: int) -> int:
        """
        Get the next calendar year that will be a leap year.
        Note if the year provided is a leap year, it will not return the same
        year.
        :param year: Reference year
        :returns: Next leap year following the reference year
        """
        next_year = year + 1
        if self.is_leap_year(next_year):
            return next_year
        else:
            return self.get_next_leap_year(next_year)

    @skill_api_method
    def is_leap_year(self, year: int) -> bool:
        """
        Check if given year is a leap year.
        :param year: Year to check
        :returns: True if the year is a leap year
        """
        return (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))

    @intent_handler(IntentBuilder("QueryTime")
                    .require("Query").require("Time")
                    .optionally("Location"))
    @intent_file_handler("what.time.is.it.intent")
    def handle_query_time(self, message: Message):
        """
        Handle a user request for the time
        :param message: Message associated with the request
        """
        if not request_for_neon(message):
            return
        location = message.data.get("Location")
        LOG.info(f"requested location: {location}")
        current_time = self.get_spoken_time(location, message)

        if not current_time:
            # An error should have been spoken by now, location wasn't valid
            return

        self.show_time_gui(location,
                           self.get_display_current_time(location),
                           self.get_display_date(location=location))
        if location:
            self.speak_dialog("TimeInLocation",
                              {"location": location.title(),
                               "time": current_time})
        else:
            self.speak_dialog("time.current", {"time": current_time})

    @intent_handler(IntentBuilder("QueryDate")
                    .require("Query").require("Date")
                    .optionally("Location"))
    def handle_query_date(self, message: Message):
        """
        Handle a user request for the date
        :param message: Message associated with the request
        """
        if not request_for_neon(message):
            return
        requested_date = self.get_local_datetime(message.data.get("Location"),
                                                 message)
        if not requested_date:
            # An error should have been spoken by now, location wasn't valid
            return
        self.show_date_gui(requested_date)
        speak = requested_date.strftime("%A, %B %-d, %Y")
        self.speak_dialog("date", {"date": speak})

    def get_timezone(self, locale: Union[str, dict]) \
            -> Optional[tzinfo]:
        """
        Use a variety of approaches to determine the intended timezone.
        :param locale: string or dict location to lookup
        :returns: datetime.tzinfo for the specified locale or default locale
        """
        LOG.info(f"Getting tz for locale: {locale}")
        str_locale = locale if isinstance(locale, str) else locale.get("city")
        # Start with known overrides, then go through available utilities
        for method in (self._get_timezone_from_table,
                       self._get_timezone_from_neon_utils,
                       self._get_timezone_from_builtins,
                       self._get_timezone_from_fuzzymatch):
            try:
                if method == self._get_timezone_from_neon_utils:
                    tz = method(locale)
                else:
                    tz = method(str_locale)
            except ValueError:
                tz = None
            if tz:
                break
        return tz

    # TODO: Homescreen creates excessive logs and won't resolve a message
    # @resolve_message
    def get_local_datetime(self, location: Optional[str] = None,
                           message: Optional[Message] = None) -> \
            Optional[datetime]:
        """
        Get the datetime at the requested location or configured location
        :param location: Optional string location to look up
        :param message: Message associated with the request
        :returns: current datetime object or None if tz not found
        """
        location = location or \
            (self._extract_location(message.data.get("utterance")) if message
             else None)

        if location:  # Lookup the tz for the requested location
            # Filter out invalid characters from location names
            location = re.sub('[?!./_-]', ' ', location)
            tz = self.get_timezone(location)
        else:  # Get the local tz
            location = self.location
            city = location['city']['name']
            state = location['city']['state']['name']
            country = location['city']['state']['country']['name']
            location = f'{city}, {state}'
            try:
                tz = pytz.timezone(self.location_timezone)
            except pytz.UnknownTimeZoneError:
                tz = None
            if not tz:  # Config tz invalid, try location lookup
                LOG.warning("configured timezone invalid or undefined")
                tz = self.get_timezone({"city": city,
                                        "state": state,
                                        "country": country})
        if not tz:
            if location and isinstance(location, str):
                self.speak_dialog("time.tz.not.found", {"location": location})
            return None

        now_utc = datetime.now(pytz.timezone('UTC'))
        return now_utc.astimezone(tz)

    def get_spoken_time(self, location: Optional[str] = None,
                        message: Optional[Message] = None) -> Optional[str]:
        """
        Get a speakable time string for the given location and request params
        :param location: optional str requested location
        :param message: optional message associated with request
        :returns: current time formatted per user preferences if location is
            valid, else None
        """
        # Get a formatted spoken time based on the user preferences
        dt = self.get_local_datetime(location, message)
        if not dt:
            return
        use_ampm = self.preference_skill(message).get('use_ampm', False)
        if location:
            use_ampm = True
        load_language(self.lang)
        return nice_time(dt, self.lang, speech=True,
                         use_24hour=self.use_24hour, use_ampm=use_ampm)

    def show_time_gui(self, location: Optional[str], display_time: str,
                      display_date: str):
        """
        Display time GUI
        :param location: optional string name of the requested location
        :param display_time: string time to display
        :param display_date: string date to display
        """
        self.gui.clear()
        LOG.info(location)
        LOG.info(display_time)
        hours, remainder = display_time.split(':')
        if "am" in remainder.lower() or "pm" in remainder.lower():
            minutes, ampm = remainder.split(' ', 1)
        else:
            minutes = remainder
            ampm = ""
        if location:
            location = location.title()
        else:
            location = ""
        if not self.preference_skill().get('use_ampm', False):
            ampm = ""
        self.gui["location"] = location
        self.gui['hours'] = hours
        self.gui['minutes'] = minutes
        self.gui['ampm'] = ampm
        self.gui['date_string'] = display_date
        self.gui.show_page('time.qml')

    def show_date_gui(self, date: datetime):
        """
        Display date GUI
        :param date: datetime object to display
        """
        self.gui.clear()
        self.gui['weekday_string'] = date.strftime("%A")
        self.gui['monthday_string'] = date.strftime("%B %-d")
        self.gui['year_string'] = date.strftime("%Y")
        self.gui.show_page('date2.qml')

    def stop(self):
        pass

    def _extract_location(self, utt: str) -> Optional[str]:
        """
        Patch the regex bug and try extracting a location from the utterance
        :param utt: string utterance
        :return: extracted location string if found in utterance
        """
        rx_file = self.find_resource('location.rx', 'regex')
        if rx_file and utt:
            with open(rx_file) as f:
                for pat in f.read().splitlines():
                    pat = pat.strip()
                    if pat and pat[0] == "#":
                        continue
                    res = re.search(pat, utt)
                    if res:
                        try:
                            to_return = res.group("Location")
                            LOG.warning("Location extracted in patch method")
                            return to_return
                        except IndexError:
                            pass
        return None

    @staticmethod
    def _get_timezone_from_neon_utils(locale: Union[dict, str]) -> \
            Optional[tzinfo]:
        """
        Lookup timezone using neon_utils
        :param locale: str location name or dict of city, state, country
        :returns: datetime.tzinfo object for the specified locale or None
        """
        if not locale:
            raise ValueError("Locale not specified")
        coords = get_coordinates(locale)
        if coords == (-1, -1):
            return None
        else:
            tz_name, _ = get_timezone(*coords)
            return pytz.timezone(tz_name)

    @staticmethod
    def _get_timezone_from_builtins(locale: str) -> \
            Optional[tzinfo]:
        """
        Lookup timezone using geocoder and TimezoneFinder
        :param locale: str location name to lookup
        :returns: datetime.tzinfo object for the specified locale or None
        """
        if not isinstance(locale, str):
            raise ValueError(f"Invalid locale specified: {locale}")
        if "/" not in locale:
            try:
                # This handles common city names, like "Dallas" or "Paris"
                # first get the lat / long.
                g = geocoder.osm(locale)
                # now look it up
                tf = TimezoneFinder()
                timezone = tf.timezone_at(lng=g.lng, lat=g.lat)
                return pytz.timezone(timezone)
            except ValueError:
                # Raised by osm and TimezoneFinder for invalid locale or coords
                pass
            except Exception as e:
                LOG.error(e)

        try:
            # This handles codes like "America/Los_Angeles"
            return pytz.timezone(locale)
        except pytz.UnknownTimeZoneError:
            pass
        except Exception as e:
            LOG.error(e)
        return None

    def _get_timezone_from_table(self, locale: str) -> \
            Optional[tzinfo]:
        """
        Lookup timezone using skill resource files
        :param locale: str location name to lookup
        :returns: datetime.tzinfo object for the specified locale or None
        """
        if not isinstance(locale, str):
            raise ValueError(f"Invalid locale specified: {locale}")
        timezones = self.translate_namedvalues("timezone.value")
        for tz in timezones:
            if locale.lower() == tz.lower():
                # assumes translation is correct
                return pytz.timezone(timezones[tz].strip())
        return None

    def _get_timezone_from_fuzzymatch(self, locale: str) -> \
            Optional[tzinfo]:
        """
        Fuzzymatch a location against the pytz timezones.
        The pytz timezones consists of Location/Name pairs.  For example:
            ["Africa/Abidjan", "Africa/Accra", ... "America/Denver", ...
             "America/New_York", ..., "America/North_Dakota/Center", ...
             "Cuba", ..., "EST", ..., "Egypt", ..., "Etc/GMT+3", ...
             "Etc/Zulu", ... "US/Eastern", ... "UTC", ..., "Zulu"]
        :param locale: str location name to lookup
        :returns: datetime.tzinfo object for the specified locale or None
        """
        if not isinstance(locale, str):
            raise ValueError(f"Invalid locale specified: {locale}")
        target = locale.lower()
        best = None
        pct = 0
        for name in pytz.all_timezones:
            # Separate at '/'
            normalized = name.lower().replace("_", " ").split("/")
            if len(normalized) == 1:
                pct = fuzzy_match(normalized[0], target)
            elif len(normalized) >= 2:
                # Check for locations like "Sydney"
                pct1 = fuzzy_match(normalized[1], target)
                # locations like "Sydney Australia" or "Center North Dakota"
                pct2 = fuzzy_match(normalized[-2] + " " + normalized[-1],
                                   target)
                pct3 = fuzzy_match(normalized[-1] + " " + normalized[-2],
                                   target)
                pct = max(pct1, pct2, pct3)
            if not best or pct >= best[0]:
                best = (pct, name)
        if best and best[0] > 0.8:
            # solid choice
            return pytz.timezone(best[1])
        elif best and best[0] > 0.3:
            say = speakable_timezone(best[1])
            if self.ask_yesno("did.you.mean.timezone",
                              data={"zone_name": say}) == "yes":
                return pytz.timezone(best[1])
        else:
            return None


def create_skill():
    return TimeSkill()
