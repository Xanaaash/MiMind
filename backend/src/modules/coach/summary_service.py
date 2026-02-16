from modules.coach.models import CoachSession


class CoachSummaryService:
    def build_summary(self, session: CoachSession) -> str:
        if not session.turns:
            return "No discussion content captured in this session."

        user_turns = [turn.message for turn in session.turns if turn.role == "user"]
        coach_turns = [turn.message for turn in session.turns if turn.role == "coach"]

        latest_user = user_turns[-1] if user_turns else ""
        latest_coach = coach_turns[-1] if coach_turns else ""

        return (
            "Session summary: "
            f"{len(user_turns)} user turns, {len(coach_turns)} coach turns. "
            f"Latest user focus: '{latest_user[:120]}'. "
            f"Latest coach response: '{latest_coach[:120]}'."
        )
