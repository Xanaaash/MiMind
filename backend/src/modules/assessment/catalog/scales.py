PHQ9 = "phq9"
GAD7 = "gad7"
PSS10 = "pss10"
CSSRS = "cssrs"

MANDATORY_SCALES = [PHQ9, GAD7, PSS10, CSSRS]

QUESTION_COUNTS = {
    PHQ9: 9,
    GAD7: 7,
    PSS10: 10,
}

# Roadmap/constitution cadence: core scales every 30 days in MVP.
REASSESSMENT_DAYS = {
    PHQ9: 30,
    GAD7: 30,
    PSS10: 30,
    CSSRS: 30,
}
