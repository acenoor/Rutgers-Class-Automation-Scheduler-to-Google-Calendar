class Course:
    
    classMap = {
        "MT" : ["Monday", "Tuesday"],
        "M" : ["Monday"],
        "MW": ["Monday", "Wednesday"],
        "MTTH": ["Monday", "Tuesday", "Thursday"],
        "MTW": ["Monday", "Tuesday", "Wednesday"],
        "MTH": ["Monday", "Thursday"],
        "MF": ["Monday", "Friday"],
        "T": ["Tuesday"],
        "TTH": ["Tuesday", "Thursday"],
        "TW": ["Tuesday", "Wednesday"],
        "TWF": ["Tuesday", "Wednesday", "Friday"],
        "TF": ["Tuesday", "Friday"],
        "TTHF": ["Tuesday", "Thursday", "Friday"],
        "W": ["Wednesday"],
        "WTH": ["Wednesday", "Thursday"],
        "WTHF": ["Wednesday", "Thursday", "Friday"],
        "WF": ["Wednesday", "Friday"],
        "TH": ["Thursday"],
        "THF": ["Thursday", "Friday"],
        "F": ["Friday"],
    }

    def __init__(self, nameOfCourse):
        self.name = nameOfCourse
        # So far, we have in one index: Dates & Timing & Location (Room and Campus)
        self.description_1 = []
        self.description_2 = []
        # [ [date, info (timing and location)], repeat of previous index but with a different date and possibly info, ...   ]
        self.total_description = []

    def get_description(self):
        return self.description_1 + self.description_2