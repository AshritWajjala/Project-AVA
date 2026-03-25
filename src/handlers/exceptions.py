class AVAException(Exception):
    """The 'Grandparent' alarm - all our specific alarms come from here."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DatabaseException(AVAException):
    """Alarm for when SQLite or Qdrant fails."""
    pass

class LLMException(AVAException):
    """Alarm for when Ollama or Groq (the brains) fails."""
    pass

class FitnessTrackerException(AVAException):
    """Alarm for when something goes wrong with your diet/weight logs."""
    pass