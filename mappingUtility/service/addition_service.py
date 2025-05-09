class AdditionService:
    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def validate(self):
        if not isinstance(self.a, (int, float)) or not isinstance(self.b, (int, float)):
            raise ValueError("Inputs must be numbers")

    def compute(self):
        self.validate()
        # Future: add logging, metrics, caching, etc.
        return self.a + self.b
