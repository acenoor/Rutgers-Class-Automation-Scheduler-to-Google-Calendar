# 'RRULE:FREQ=WEEKLY;UNTIL=<YYYYMMDD>' <- depending on semester

event = {
  'summary': '',
  'location': '',
  'description': '',
  'start': {
    'dateTime': '',
    'timeZone': 'America/New_York',
  },
  'end': {
    'dateTime': '',
    'timeZone': 'America/New_York',
  },
  'recurrence': [
    'RRULE:FREQ=WEEKLY;UNTIL=<YYYYMMDD>'
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 60},
    ],
  },
}