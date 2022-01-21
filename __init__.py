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
import time

from astral import Astral
from mycroft.skills import skill_api_method
from pytz import timezone
from neon_utils.location_utils import *
from adapt.intent import IntentBuilder
from neon_utils.skills.neon_skill import NeonSkill, LOG

import mycroft.audio
from mycroft.skills.core import intent_handler
from mycroft.util.format import nice_time, date_time_format


class TimeSkill(NeonSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.astral = Astral()
        self.displayed_time = None
        self.display_tz = None
        self.answering_query = False

    def initialize(self):
        pass

    def use_24hour(self, message=None) -> bool:
        return self.preference_unit(message)['time'] == 24

    def get_timezone(self, locale):
        try:
            # TODO: Return the location name like weather skill to disambiguate DM
            lat, lng = get_coordinates(locale)
            # city, county, state, country = LookupHelpers.get_location(lat, lng)
            time_zone, _ = get_timezone(lat, lng)
            # time_zone = self.tzfinder.timezone_at(lng=float(lng), lat=float(lat))
            return timezone(time_zone)
        except Exception as e:
            LOG.error(e)
        try:
            # Fallback Attempt using astral
            return timezone(self.astral[locale].timezone)
        except Exception as e:
            LOG.error(e)
        try:
            # This handles codes like "America/Los_Angeles"
            return timezone(locale)
        except Exception as e:
            LOG.error(e)
            return None

    def get_local_datetime(self, location, message) -> datetime:
        now_utc = datetime.now(timezone('UTC'))
        pref_location = self.preference_location(message)
        try:
            tz = timezone(pref_location['tz'])
        except Exception as e:
            LOG.error(e)
            tz = None
        if location:
            # Filter out invalid characters from location names
            location = re.sub('[?!./_-]', ' ', location)
            tz = self.get_timezone(location)
        elif not tz:
            LOG.warning("timezone invalid or undefined!")
            try:
                tz = self.get_timezone({"city": pref_location["city"],
                                        "state": pref_location["state"],
                                        "country": pref_location["country"]})
                location = f'{pref_location["city"]}, {pref_location["state"]}, {pref_location["country"]}'
            except Exception as e:
                LOG.warning(e)
        if not tz:
            if location and isinstance(location, str):
                self.speak_dialog("time.tz.not.found", {"location": location})
            return None

        return now_utc.astimezone(tz)

    def get_spoken_time(self, message, location=None):
        # Get a formatted spoken time based on the user preferences
        dt = self.get_local_datetime(location, message)
        if not dt:
            return
        use_ampm = self.preference_skill(message)['use_ampm']
        if location:
            use_ampm = True
        return nice_time(dt, self.lang, speech=True,
                         use_24hour=self.use_24hour(message), use_ampm=use_ampm)

    @skill_api_method
    def get_display_date(self, day=None, location=None):
        """Get the full date in the configured format.
        Args:
            day (datetime): optional - datetime object
            location (str): optional - location to get the current datetime of

        Returns:
            Str: The full date in the user configured format - DMY or MDY
        """
        if not day:
            day = self.get_local_datetime(location, None)
        if self.preference_unit().get('date') == 'MDY':
            return day.strftime("%-m/%-d/%Y")
        elif self.preference_unit().get('date') == 'YMD':
            return day.strftime("%Y/%-m/%-d")
        else:
            return day.strftime("%Y/%-d/%-m")

    @skill_api_method
    def get_display_current_time(self, location=None, dtUTC=None):
        """Get a formatted digital clock time based on the user preferences
        Args:
            location (str): optional - location to get the current datetime of
            dtUTC (datetime): optional - current UTC datetime

        Returns:
            Str: The full date in the user configured format - DMY or MDY
        """
        try:
            dt = self.get_local_datetime(location, dtUTC)
            if not dt:
                return None

            return nice_time(dt, self.lang, speech=False, use_24hour=self.use_24hour(),
                             use_ampm=self.preference_skill()['use_ampm'])
        except Exception as e:
            LOG.error(e)
            return None

    @skill_api_method
    def get_weekday(self, day=None, location=None):
        """Get the weekday name for a given day.

        Args:
            day (datetime): optional - datetime object
            location (str): optional - location to get the current datetime of

        Returns:
            Str: The name of the weekday eg Monday
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
    def get_month_date(self, day=None, location=None):
        """Get the date and month for a given day.
        Args:
            day (datetime): optional - datetime object
            location (str): optional - location to get the current datetime of

        Returns:
            Str: The date in the format DD MONTH or MONTH DD
                 depending on the users date_format setting.
        """
        if not day:
            day = self.get_local_datetime(location, None)
        if self.lang in date_time_format.lang_config.keys():
            localized_month_names = date_time_format.lang_config[self.lang]['month']
            month = localized_month_names[str(int(day.strftime("%m")))]
        else:
            month = day.strftime("%B")
        month = month.capitalize()
        if self.preference_unit().get('date') == 'MDY':
            return "{} {}".format(month, day.strftime("%d"))
        else:
            return "{} {}".format(day.strftime("%d"), month)

    @skill_api_method
    def get_year(self, day=None, location=None):
        """Get the year for a given day in the devices local time.

        Args:
            day (datetime): optional - datetime object
            location (str): optional - location to get the current datetime of

        Returns:
            Str: The year in the format YYYY
        """
        if not day:
            day = self.get_local_datetime(location, None)
        return day.strftime("%Y")

    @skill_api_method
    def get_next_leap_year(self, year):
        """Get the next calendar year that will be a leap year.
        Note if the year provided is a leap year, it will not return the same
        year.
        Args:
            year (int): Reference year
        Returns:
            Int: Next leap year following the reference year
        """
        next_year = year + 1
        if self.is_leap_year(next_year):
            return next_year
        else:
            return self.get_next_leap_year(next_year)

    @skill_api_method
    def is_leap_year(self, year):
        """Check if given year is a leap year.
        Args:
            year (int): Year to check
        Returns
            Bool: True if the year is a leap year
        """
        return (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))

    @intent_handler(IntentBuilder("").require("Query").require("Time").
                    optionally("Location"))
    def handle_query_time(self, message):
        location = message.data.get("Location")
        LOG.info(f"time location: {location}")
        # Looks like this takes america/los_angeles for a location
        current_time = self.get_spoken_time(message, location)

        if not current_time:
            return

        # speak it
        if location:
            self.speak_dialog("TimeInLocation", {"location": location.title(), "time": current_time})
        else:
            self.speak_dialog("time.current", {"time": current_time})

        # and briefly show the time
        self.answering_query = True
        time.sleep(5)
        mycroft.audio.wait_while_speaking()
        self.answering_query = False
        self.displayed_time = None
        if self.gui_enabled:
            self.show_time_gui(location,
                               self.get_display_current_time(location),
                               self.get_display_date(location=location), message)

    def show_time_gui(self, location, display_time, display_date, message):
        """ Display time on the Mycroft GUI. """
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
        if not self.preference_skill(message)['use_ampm']:
            ampm = ""
        self.gui["location"] = location
        self.gui['hours'] = hours
        self.gui['minutes'] = minutes
        # self.gui['time_string'] = display_time
        self.gui['ampm'] = ampm
        self.gui['date_string'] = display_date
        self.gui.show_page('time.qml')

    def show_date_gui(self, date: datetime):
        self.gui.clear()
        # self.gui['date_string'] = date_string
        self.gui['weekday_string'] = date.strftime("%A")
        self.gui['monthday_string'] = date.strftime("%B %-d")
        self.gui['year_string'] = date.strftime("%Y")
        self.gui.show_page('date2.qml')
        self.clear_gui_timeout(10)

    @intent_handler(IntentBuilder("").require("Query").require("Date").
                    optionally("Location"))
    def handle_query_date(self, message):
        local_date = self.get_local_datetime(message.data.get("Location"), message)
        if not local_date:
            return
        speak = local_date.strftime("%A, %B %-d, %Y")
        self.speak_dialog("date", {"date": speak})

        if self.gui_enabled:
            self.show_date_gui(local_date)

    def stop(self):
        pass


def create_skill():
    return TimeSkill()
