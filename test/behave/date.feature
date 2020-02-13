Feature: Date Time Skill Date functionality

  Scenario Outline: what's the date
    Given an english speaking user
     When the user says "<whats the date>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: whats the date
    | whats the date |
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

  Scenario Outline: what will the date be in the future
    Given an english speaking user
     When the user says "<whats the future date>"
     Then "mycroft-date-time" should reply with dialog from "date.relative.future.dialog"

  Examples: whats the future date
    | whats the future date |
    | what's tomorrow's date |
    | what is the date tomorrow |
    | what date is next monday |
    | what is the date this Monday |
    | what is the date 5 days from now |
    | what is the date a week from now |
    | what is the date a week from today |
    | what is the date 5 days from today |

  Scenario Outline: what was a date from the past
    Given an english speaking user
     When the user says "<what was a date from the past>"
     Then "mycroft-date-time" should reply with dialog from "date.relative.past.dialog"

  Examples: what was a date from the past
    | what was a date from the past |
    | what was yesterday's date |
    | what was the date yesterday |
    | what was the date last monday |
    | what was the date last weekend |
    | what was the date a week ago |
    | what was the date a week ago today |
    | what was the date 5 days ago |

  Scenario Outline: when is a date
    Given an english speaking user
     When the user says "<when is a date>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: when is a date
    | when is a date |
    | when is the 1st of september |
    | what day of the week will it be on september 1st 2020 |
    | what day is september 1st 2020 |
    | what day was it november 1st 1953 |
    | when was november 1st 1953 |
    | when is June 30th |
    | what day is in June 30th |

  Scenario Outline: when is a holiday
    Given an english speaking user
     When the user says "<when is a holiday>"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Examples: when is a holiday
    | when is a holiday |
    | when is christmas |
    | when is christmas 2020 |
    | when is christmas 2030 |
    | what day of the week is 4th of July |
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

  Examples: when is a holiday
     | what is the date next weekend |
     | what date is next weekend |
     | what dates are next weekend |
     | what is the date next weekend |

  Scenario Outline: what was the date last weekend
    Given an english speaking user
     When the user says "<what was the date last weekend>"
     Then "mycroft-date-time" should reply with dialog from "date.last.weekend.dialog"

  Examples: when is a holiday
    | what was the date last weekend |
    | what date was it last weekend |
    | what dates were last weekend |

  Scenario Outline: next leap year
    Given an english speaking user
     When the user says "<when is the next leap year>"
     Then "mycroft-date-time" should reply with dialog from "next.leap.year.dialog"

  Examples: when is a holiday
    | when is the next leap year |
    | what year is the next leap year |
    | when is leap year |
