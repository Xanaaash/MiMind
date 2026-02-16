PHQ9 = "phq9"
GAD7 = "gad7"
PSS10 = "pss10"
CSSRS = "cssrs"
SCL90 = "scl90"

MANDATORY_SCALES = [PHQ9, GAD7, PSS10, CSSRS]
SUPPORTED_CLINICAL_SCALES = MANDATORY_SCALES + [SCL90]

QUESTION_COUNTS = {
    PHQ9: 9,
    GAD7: 7,
    PSS10: 10,
    SCL90: 90,
}

# Roadmap/constitution cadence: core scales every 30 days in MVP.
REASSESSMENT_DAYS = {
    PHQ9: 30,
    GAD7: 30,
    PSS10: 30,
    CSSRS: 30,
    SCL90: 90,
}

SCL90_DIMENSIONS = [
    "somatization",
    "obsessive_compulsive",
    "interpersonal_sensitivity",
    "depression",
    "anxiety",
    "hostility",
    "phobic_anxiety",
    "paranoid_ideation",
    "psychoticism",
]
