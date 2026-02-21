PHQ9 = "phq9"
GAD7 = "gad7"
PSS10 = "pss10"
CSSRS = "cssrs"
SCL90 = "scl90"
WHO5 = "who5"
ISI7 = "isi7"
SWLS5 = "swls5"
UCLA3 = "ucla3"
CDRISC10 = "cdrisc10"
PHQ15 = "phq15"

MANDATORY_SCALES = [PHQ9, GAD7, PSS10, CSSRS]
SUPPORTED_CLINICAL_SCALES = MANDATORY_SCALES + [SCL90, WHO5, ISI7, SWLS5, UCLA3, CDRISC10, PHQ15]

QUESTION_COUNTS = {
    PHQ9: 9,
    GAD7: 7,
    PSS10: 10,
    SCL90: 90,
    WHO5: 5,
    ISI7: 7,
    SWLS5: 5,
    UCLA3: 3,
    CDRISC10: 10,
    PHQ15: 15,
}

# Roadmap/constitution cadence: core scales every 30 days in MVP.
REASSESSMENT_DAYS = {
    PHQ9: 30,
    GAD7: 30,
    PSS10: 30,
    CSSRS: 30,
    SCL90: 90,
    WHO5: 30,
    ISI7: 30,
    SWLS5: 60,
    UCLA3: 60,
    CDRISC10: 60,
    PHQ15: 45,
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
