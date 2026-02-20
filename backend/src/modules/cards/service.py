from modules.tests.models import TestDefinition, TestResult


class ShareCardService:
    def build_share_card(self, definition: TestDefinition, result: TestResult) -> dict:
        primary = ""
        if "type" in result.summary:
            primary = str(result.summary["type"])
        elif "primary_style" in result.summary:
            primary = str(result.summary["primary_style"])
        elif "dominant_trait" in result.summary:
            primary = str(result.summary["dominant_trait"])

        return {
            "format": "vertical",
            "title": definition.display_name,
            "subtitle": f"My result: {primary}" if primary else "My latest result",
            "result_id": result.result_id,
            "share_text": f"I completed {definition.display_name} on MiMind.",
        }
