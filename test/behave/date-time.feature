Feature: mycroft-date-time

  Scenario Outline: what time is it
    Given an english speaking user
     When the user says "<what time is it>"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Examples: what time examples
    | what time is it |
    | what's the time |
    | whats the time |

  Scenario: what's the time going to be later
    Given an english speaking user
     When the user says "what will the time be in seven hours"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Scenario: what's the time in place
    Given an english speaking user
     When the user says "what time is it in paris"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Scenario: later time in location
    Given an english speaking user
     When the user says "what time will it be in paris in 30 minutes"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Scenario: what date
    Given an english speaking user
     When the user says "whats the date"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Scenario: what was the date previously
    Given an english speaking user
     When the user says "what was the date last tuesday"
     Then "mycroft-date-time" should reply with dialog from "date.relative.past.dialog"

  Scenario: what will the date be in the future
    Given an english speaking user
     When the user says "whats the date next tuesday"
     Then "mycroft-date-time" should reply with dialog from "date.relative.future.dialog"

  Scenario: when is date
    Given an english speaking user
     When the user says "when is the 1st of september"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Scenario: when is holiday
    Given an english speaking user
     When the user says "what date is christmas"
     Then "mycroft-date-time" should reply with dialog from "date.dialog"

  Scenario: next weekend date
    Given an english speaking user
     When the user says "what is the date next weekend"
     Then "mycroft-date-time" should reply with dialog from "date.future.weekend.dialog"

  Scenario: last weekend date
    Given an english speaking user
     When the user says "what was the date last weekend"
     Then "mycroft-date-time" should reply with dialog from "date.last.weekend.dialog"

  Scenario: next leap year
    Given an english speaking user
     When the user says "when is the next leap year"
     Then "mycroft-date-time" should reply with dialog from "next.leap.year.dialog"
