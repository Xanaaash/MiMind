from datetime import date, timedelta

from modules.assessment.catalog.scales import REASSESSMENT_DAYS
from modules.assessment.models import ReassessmentSchedule


def build_reassessment_schedule(start_date: date) -> ReassessmentSchedule:
    due_dates = {}
    for scale, days in REASSESSMENT_DAYS.items():
        due_dates[scale] = start_date + timedelta(days=days)
    return ReassessmentSchedule(due_dates=due_dates)
