from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- LOG TEMPLATE 1: FITNESS ---
class FitnessLog(BaseModel):
    weight: Optional[float] = Field(None, description="Body weight in kg")
    calories: Optional[int] = Field(None, description="Total calories")
    protein: Optional[int] = Field(None, description="Protein in grams")
    
class Exercise(BaseModel):
    exercise: str = Field(..., description="Name of the exercise (e.g., Bench Press)")
    sets: int = Field(..., description="Number of sets")
    reps: int = Field(..., description="Number of reps")
    weight: float = Field(default=0.0, description="Weight used in kg")

# --- LOG TEMPLATE 2: WORKOUT ---
class WorkoutLog(BaseModel):
    workout_type: str = Field(..., description="e.g., Push, Pull, Legs")
    exercises: List[Exercise] 

    
# --- LOG TEMPLATE 3: JOURNAL ---
class JournalLog(BaseModel):
    content: str = Field(..., description="The user's thoughts or reflections")
    mood: str = Field(..., description="Mood level: Low, Meh, Neutral, Good, Great")
    tags: List[str] = Field(default_factory=list, description="Relevant keywords for the entry")

