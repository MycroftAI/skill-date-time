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

import re


def speakable_timezone(tz):
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