Feature: Date Time Skill Date functionality

  Scenario Outline: what's the date
    Given an english speaking user
     When the user says "<what's the date>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: whats the date
    | what's the date |
    | what date is it |
    | what's today's date |
    | what's the date |
    | what's the date today |
    | what day of the month is it |
    | today's date is what |
    | what day is it |
    | what day is it today |
    | what's today |
    | what is today |
    | what's the day |
    | today's day is what |
    | today is what day |
    | what is the day of the week |
    | what is the day of the month |
    | what is the day |

  Scenario Outline: what is the date a number of days in the future
    Given an english speaking user
     When the user says "<what's the date in 2 days>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: what is the date a number of days in the future
    | what's the date in 2 days |
    | what is the date 5 days from now |
    | what is the date a week from now |
    | what is the date a week from today |
    | what is the date 5 days from today |

  Scenario Outline: what was the date a number of days in the past
    Given an english speaking user
     When the user says "<what was the date 2 days ago>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: what was the date a number of days in the past
    | what was the date 2 days ago |
    | what was the date 2 days ago |
    | what was the date a week ago |
    | what was the date a week ago today |
    | what was the date 5 days ago |

  Scenario Outline: when is a date in the future
    Given an english speaking user
     When the user says "<what day is future date>"
     Then "mycroft-date-time" should reply with dialog from "date.relative.future.dialog"

  Examples: when is a date

    | what day is future date |
    | when is the 1st of september |
    | when is June 30th |
    | what's tomorrow's date |
    | what is the date tomorrow |
    | what date is next monday |
    | what is the date this Monday |

  @xfail
  # Jira 103 https://mycroft.atlassian.net/browse/MS-103
  Scenario Outline: Failing when is a date in the future
    Given an english speaking user
     When the user says "<what day is future date>"
     Then "mycroft-date-time" should reply with dialog from "date.relative.future.dialog"

  Examples: when is a date
    | what day is future date |
    | what day is september 1st 2028 |
    | what day is June 30th |

  Scenario Outline: when is a date in the past
    Given an english speaking user
     When the user says "<what day was it november 1st 1953>"
     Then "mycroft-date-time" should reply with dialog from "date.relative.past.dialog"

    | what day was it november 1st 1953 |
    | what day was it november 1st 1953 |
    | when was november 1st 1953 |
    | what was the date last monday |
    | what was yesterday's date |
    | what was the date yesterday |

  @xfail
  # Jira 104 https://mycroft.atlassian.net/browse/MS-105
  Scenario Outline: when is a holiday
    Given an english speaking user
     When the user says "<when is new year's day>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: when is a holiday
    | when is new year's day |
    | when is christmas |
    | when is christmas 2020 |
    | when is christmas 2030 |
    | when is thanksgiving 2020 |
    | how many days until christmas |
    | how many days until christmas |
    | how long until thanksgiving |
    | what day is thanksgiving this year |
    | when is ramadan 2020 |

  Scenario Outline: what is the date next weekend
    Given an english speaking user
     When the user says "<what is the date next weekend>"
     Then "mycroft-date-time" should reply with dialog from "date.future.weekend.dialog"

  Examples: what is the date next weekend
     | what is the date next weekend |
     | what date is next weekend |
     | what dates are next weekend |
     | what is the date next weekend |

  Scenario Outline: what was the date last weekend
    Given an english speaking user
     When the user says "<what was the date last weekend>"
     Then "mycroft-date-time" should reply with dialog from "date.last.weekend.dialog"

  Examples: what was the date last weekend
    | what was the date last weekend |
    | what was the date last weekend |
    | what dates were last weekend |

  @xfail
  # Jira 106 https://mycroft.atlassian.net/browse/MS-106
  Scenario Outline: Failing what was the date last weekend
    Given an english speaking user
     When the user says "<what was the date last weekend>"
     Then "mycroft-date-time" should reply with dialog from "date.last.weekend.dialog"

  Examples: what was the date last weekend
    | what was the date last weekend |
    | what date was it last weekend |

  @xfail
  # Jira 107 https://mycroft.atlassian.net/browse/MS-107
  Scenario Outline: when is the next leap year
    Given an english speaking user
     When the user says "<when is the next leap year>"
     Then "mycroft-date-time" should reply with dialog from "next.leap.year.dialog"

  Examples: when is the next leap year
    | when is the next leap year |
    | what year is the next leap year |
    | when is leap year |
