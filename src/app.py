"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
    ,
    "Basketball Team": {
        "description": "Competitive basketball practices and games",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["sam@mergington.edu", "lisa@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Recreational soccer matches and training",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting workshops and school productions",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Formal debating and public speaking practice",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["sara@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and science projects",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["liam@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Normalize the email for consistent comparisons/storage
    normalized_email = email.strip().lower()

    # Prevent duplicate signups
    existing = [p.strip().lower() for p in activity.get("participants", [])]
    if normalized_email in existing:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Enforce max participants if present
    max_participants = activity.get("max_participants")
    if isinstance(max_participants, int) and len(activity.get("participants", [])) >= max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity.setdefault("participants", []).append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participant")
def remove_participant(activity_name: str, email: str):
    """Remove a participant from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity.get("participants", [])

    # Normalize the email for consistent comparison
    normalized_email = email.strip().lower()

    # Find and remove the participant (case-insensitive)
    for i, p in enumerate(participants):
        if p.strip().lower() == normalized_email:
            participants.pop(i)
            return {"message": f"Removed {normalized_email} from {activity_name}"}

    # Participant not found
    raise HTTPException(status_code=404, detail="Participant not found in this activity")
