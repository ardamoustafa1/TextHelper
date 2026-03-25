from collections import Counter
from typing import Dict, List

from app.models.schemas import Suggestion


class Telemetry:
    """
    Lightweight, in-memory telemetry for suggestion behaviour.
    Can be exported to real monitoring later.
    """

    def __init__(self) -> None:
        self.total_requests = 0
        self.suggestions_shown_total = 0
        self.suggestions_accepted_total = 0
        self.keystrokes_saved_total = 0
        self.by_source_shown: Counter = Counter()
        self.by_source_accepted: Counter = Counter()

    def record_impressions(self, suggestions: List[Suggestion]) -> None:
        self.total_requests += 1
        count = len(suggestions)
        self.suggestions_shown_total += count
        for s in suggestions:
            self.by_source_shown[s.source] += 1

    def record_accept(
        self,
        user_id: str,
        text: str,
        selected: str,
        source: str = "unknown",
    ) -> None:
        self.suggestions_accepted_total += 1
        self.by_source_accepted[source] += 1

        # Approximate keystroke savings: full word - last token length
        try:
            prefix = (text or "").split()[-1] if text else ""
            saved = max(len(selected) - len(prefix), 0)
            self.keystrokes_saved_total += saved
        except Exception:
            pass

    def snapshot(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "suggestions_shown_total": self.suggestions_shown_total,
            "suggestions_accepted_total": self.suggestions_accepted_total,
            "keystrokes_saved_total": self.keystrokes_saved_total,
            "by_source_shown": dict(self.by_source_shown),
            "by_source_accepted": dict(self.by_source_accepted),
        }


telemetry = Telemetry()

