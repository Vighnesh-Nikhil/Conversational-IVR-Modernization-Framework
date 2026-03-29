"""
=====================================================================
Module 2: Integration Layer Development
Project: Conversational IVR Modernization Framework
Use Case: Hospital Lab Services IVR
Approach: Web Simulator (Backend Middleware Implementation)

OBJECTIVE:
Build a middleware/API layer that connects a legacy menu-driven IVR 
system to a modern Conversational AI stack (ACS/Twilio/BAP ready).

This backend acts as an integration layer between:
- IVR Interface (DTMF simulation)
- Backend Hospital Database
- Future Conversational AI Engine

---------------------------------------------------------------------
WORKFLOW OVERVIEW

Step 1: IVR sends request to /start-call
Step 2: Middleware creates session and returns welcome prompt
Step 3: IVR sends user input to /handle-menu
Step 4: Middleware routes input based on menu logic
Step 5: Backend services are triggered (lab report lookup, info retrieval)
Step 6: Middleware returns real-time response
Step 7: Session ends or continues

This demonstrates:
- Middleware/API connector implementation
- Real-time data handling
- Session management
- Sample transaction validation
=====================================================================
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uuid

# ================================================================
# CONFIGURATION SECTION
# ================================================================

APP_NAME = "Hospital Lab Services IVR Middleware"
VERSION = "2.0"

app = FastAPI(title=APP_NAME)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# SIMULATED BACKEND DATABASE
# ================================================================

LAB_REPORT_DATABASE = {
    "3001": {"patient_name": "Rahul", "status": "Ready for collection"},
    "3002": {"patient_name": "Anita", "status": "Under Processing"},
    "3003": {"patient_name": "Suresh", "status": "Emailed to registered address"}
}

# ================================================================
# SESSION MANAGEMENT
# ================================================================

sessions = {}

# ================================================================
# REQUEST MODELS
# ================================================================

class StartCallRequest(BaseModel):
    caller_name: str = "Guest"

class MenuInputRequest(BaseModel):
    session_id: str
    user_input: str

# ================================================================
# HEALTH CHECK ENDPOINT
# ================================================================

@app.get("/")
def health_check():
    return {
        "application": APP_NAME,
        "version": VERSION,
        "status": "Middleware Running"
    }

# ================================================================
# START CALL (WELCOME PROMPT)
# ================================================================

@app.post("/start-call")
def start_call(request: StartCallRequest):

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "current_menu": "main_menu",
        "caller_name": request.caller_name
    }

    welcome_message = (
        f"Welcome to Hospital Lab Services, {request.caller_name}. "
        "Press 1 to check Lab Report Status. "
        "Press 2 for Lab Working Hours. "
        "Press 3 for Contact Support. "
        "Press 4 for Sample Collection Information. "
        "Press 5 to request Email Copy of Report. "
        "Press 9 to Exit."
    )

    return {
        "session_id": session_id,
        "message": welcome_message
    }

# ================================================================
# MENU HANDLING LOGIC
# ================================================================

@app.post("/handle-menu")
def handle_menu(input_data: MenuInputRequest):

    session = sessions.get(input_data.session_id)

    if not session:
        return {"error": "Invalid session. Please restart call."}

    current_menu = session["current_menu"]

    # ---------------- MAIN MENU ----------------

    if current_menu == "main_menu":

        if input_data.user_input == "1":
            session["current_menu"] = "lab_report_menu"
            return {
                "message": "Please enter your Patient ID to retrieve report status."
            }

        elif input_data.user_input == "2":
            return {
                "message": "Lab Working Hours: Monday to Saturday, 8 AM to 8 PM."
            }

        elif input_data.user_input == "3":
            return {
                "message": "You can contact lab support at 1800-123-456."
            }

        elif input_data.user_input == "4":
            return {
                "message": "Sample collection is available from 7 AM to 11 AM. Please carry valid ID proof."
            }

        elif input_data.user_input == "5":
            return {
                "message": "To receive your lab report via email, please ensure your email is registered with the hospital."
            }

        elif input_data.user_input == "9":
            sessions.pop(input_data.session_id)
            return {
                "message": "Thank you for calling. Goodbye.",
                "call_status": "Ended"
            }

        else:
            return {
                "message": "Invalid option selected. Please try again."
            }

    # ---------------- LAB REPORT MENU ----------------

    elif current_menu == "lab_report_menu":

        patient_id = input_data.user_input
        report_data = LAB_REPORT_DATABASE.get(patient_id)

        if report_data:
            sessions.pop(input_data.session_id)

            return {
                "message": (
                    f"Hello {report_data['patient_name']}. "
                    f"Your lab report status is: {report_data['status']}."
                ),
                "call_status": "Completed"
            }
        else:
            return {
                "message": "Invalid Patient ID. Please enter correct ID."
            }

# ---------------------------------------------------------
# Conversational AI Layer (Milestone 3)
# ---------------------------------------------------------
# This layer allows users to interact with the IVR system
# using natural language instead of pressing keypad digits.
#
# Flow:
# User Text → Intent Detection → Map to IVR Option → Handle Menu
# ---------------------------------------------------------

import re

def detect_intent(text: str):
    """
    Detects user intent from natural language input
    and maps it to IVR menu options.
    """
    # Direct digit input handling (for IVR keypad)
    if text.strip() in ["1","2","3","4","5","9"]:
        return text.strip()
    text = text.lower()

    # ---------------------------------
    # Entity Extraction (Patient ID)
    # ---------------------------------
    match = re.search(r"\b\d{4,}\b", text)
    if match:
        return "patient_id:" + match.group()

    # ---------------------------------
    # Intent Detection (Keyword Based)
    # ---------------------------------

    # Lab Report Status
    if any(word in text for word in ["report", "lab report", "report status"]):
        return "1"

    # Lab Working Hours
    elif any(word in text for word in ["hour", "timing", "working hours"]):
        return "2"

    # Contact Support
    elif any(word in text for word in ["support", "help", "contact"]):
        return "3"

    # Sample Collection Info
    elif any(word in text for word in ["sample", "collection"]):
        return "4"

    # Email Report
    elif any(word in text for word in ["email", "mail"]):
        return "5"

    # Exit
    elif any(word in text for word in ["exit", "quit"]):
        return "9"

    # Unknown intent
    return None


# ---------------------------------------------------------
# Conversational Endpoint
# ---------------------------------------------------------
# This endpoint accepts natural language input
# and routes it to existing IVR logic
# ---------------------------------------------------------

@app.post("/converse")
def converse(session_id: str, user_text: str):
    """
    Converts user natural language into IVR actions
    """

    # Detect intent
    result = detect_intent(user_text)

    # If nothing understood
    if result is None:
        return {
            "message": "Sorry, I didn't understand that. You can ask about lab reports, timings, support, or sample collection."
        }

    # ---------------------------------
    # If Patient ID detected
    # ---------------------------------
    if result.startswith("patient_id:"):
        patient_id = result.split(":")[1]

        input_data = MenuInputRequest(
            session_id=session_id,
            user_input=patient_id
        )

        return handle_menu(input_data)

    # ---------------------------------
    # Normal intent → map to menu digit
    # ---------------------------------
    input_data = MenuInputRequest(
        session_id=session_id,
        user_input=result
    )

    return handle_menu(input_data)
# -------------------------------
# Start Session Endpoint
# -------------------------------

import uuid

sessions = {}

@app.get("/start")
def start_call(caller_name: str):
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "caller_name": caller_name
    }

    return {
        "session_id": session_id,
        "message": f"Welcome {caller_name}, how can I assist you?"
    }
