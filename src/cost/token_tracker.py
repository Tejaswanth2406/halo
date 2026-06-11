class TokenTracker:

    def __init__(self):
        self.usage = {}

    def track(
        self,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        session_id: str = "default"
    ) -> None:

        key = (user_id, session_id, model)

        if key not in self.usage:
            self.usage[key] = {
                "input_tokens": 0,
                "output_tokens": 0
            }

        self.usage[key]["input_tokens"] += input_tokens
        self.usage[key]["output_tokens"] += output_tokens