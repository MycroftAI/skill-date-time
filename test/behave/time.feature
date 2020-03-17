Feature: Date Time Skill Time functionality

  Scenario Outline: what time is it
    Given an english speaking user
     When the user says "<what time is it>"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Examples: what time examples
    | what time is it |
    | clock |
    | time |
    | what's the time |
    | whats the time |
    | what time is it |
    | tell me the time |
    | the time please |
    | current time |
    | time please |
    | give me the time |
    | give me the current time |
    | tell me what time it is |
    | tell me the current time |
    | what time is it currently |
    | time right now |
    | what is the time |
    | what time is it now |
    | do you know what time it is |
    | could you tell me the time please |
    | excuse me what's the time |
    | what is the current time |
    | what's the current time |
    | what time |

  @xfail
  # jira MS-99 https://mycroft.atlassian.net/browse/MS-99
  Scenario Outline: Failing what time is it
    Given an english speaking user
     When the user says "<what time is it>"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Examples: what time examples
    | what time is it |
    | check the time |
    | check time |
    | check clock |


  Scenario Outline: what's the time in a location
    Given an english speaking user
     When the user says "<what is the time in a location>"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Examples: what time examples
    | what is the time in a location |
    | what's the time in paris |
    | what's the time in london |

  @xfail
  # jira MS-100 https://mycroft.atlassian.net/browse/MS-100
  Scenario Outline: Failing what's the time in a location
    Given an english speaking user
     When the user says "<what is the time in a location>"
     Then "mycroft-date-time" should reply with dialog from "time.current.dialog"

  Examples: what time examples
    | what is the time in a location |
    | check the time in Washington DC |
    | what's the current time in Italy |
    | what's the time in russia |
    | what time is it in washington |

  Scenario Outline: What's the time in a location when Mycroft needs more information
    Given an english speaking user
    When the user says "<what is the time in a location that needs more information>"
    Then "mycroft-date-time" should reply with dialog from "did.you.mean.timezone.dialog"
    Then the user says "<yes>"

    | what is the time in a location that needs more information | yes |
    | what's the time in washington | yes |
    | what time is it in washington | no |
    | what is the time in washington | nevermind |

  Scenario Outline: what's the future time
    Given an english speaking user
     When the user says "<what time will it be in 8 hours>"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Examples: what's the future time
    | what time will it be in 8 hours |
    | what time will it be 8 hours from now |
    | give me the time 8 hours from now |
    | the time 8 hours from now please |
    | what's the time in 8 hours |
    | what will be the time in 8 hours |
    | when is it 8 hours from now |
    | in 8 hours what time will it be |
    | what time will it be in 36 hours |
    | what time will it be in 90 minutes |
    | in 97 minutes what time will it be |
    | what time will it be in 60 seconds |

  @xfail
  # jira MS-101 https://mycroft.atlassian.net/browse/MS-101
  Scenario Outline: Failing what's the future time
    Given an english speaking user
     When the user says "<what time will it be in 8 hours>"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Examples: what's the future time
    | what time will it be in 8 hours |
    | what's the time 8 hours from now |

  Scenario Outline: what's the future time in a location
    Given an english speaking user
     When the user says "<what time will it be in the future in a location>"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Examples: what time will it be in the future in a location
     | what time will it be in the future in a location |
     | what time will it be in 8 hours in Berlin |
     | what time will it be 8 hours from now in Paris |
     | what's the time in Los Angeles 8 hours from now |

  @xfail
  # jira MS-102 https://mycroft.atlassian.net/browse/MS-102
  Scenario Outline: Failing what's the future time in a location
    Given an english speaking user
     When the user says "<what time will it be in the future in a location>"
     Then "mycroft-date-time" should reply with dialog from "time.future.dialog"

  Examples: what time will it be in the future in a location
     | what time will it be in the future in a location |
     | give me the time 8 hours from now in Italy |
     | what's the time in France 8 hours |
     | what will be the time in Kansas in 8 hours |
     | the time 8 hours from in New York City please |
