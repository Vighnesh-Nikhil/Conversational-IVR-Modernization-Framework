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
# ---------------------------------------------------------
# Milestone 3: Conversational AI Interface Layer
#
# This layer enables natural language interaction with the
# IVR system. Instead of pressing keypad digits, users can
# enter requests in conversational form.
#
# Architecture Flow:
# User Natural Language Input
#        ↓
# Intent Detection (Keyword + Pattern Matching)
#        ↓
# Entity Extraction (e.g., Patient ID)
#        ↓
# Mapping to Existing IVR Menu Options
#        ↓
# Routing to Legacy Menu Handler
#        ↓
# Existing IVR Logic Executes
#
# This approach preserves the existing IVR architecture
# while introducing a conversational interface on top.
# ---------------------------------------------------------

from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import re
# ================================================================
# CONFIGURATION SECTION
# ================================================================

APP_NAME = "Hospital Lab Services IVR Middleware"
VERSION = "2.0"

app = FastAPI(title=APP_NAME)

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
# This function detects the user's intent from natural
# language input and maps it to the corresponding IVR
# menu option used in the existing system.
# ---------------------------------------------------------

def detect_intent(text: str):
    # Convert input text to lowercase for easier matching
    text = text.lower()
    # Detect patient ID numbers (5+ digits)
    match = re.search(r"\b\d{5,}\b", text)
    if match:
        return "patient_id:" + match.group()

    # Intent: Lab Report Status
    if any(word in text for word in ["report", "lab report", "report status"]):
        return "1"

    # Intent: Lab Working Hours
    elif any(word in text for word in ["hour", "timing", "working hours"]):
        return "2"

    # Intent: Contact Support
    elif any(word in text for word in ["support", "help", "contact"]):
        return "3"

    # Intent: Sample Collection Information
    elif any(word in text for word in ["sample", "collection"]):
        return "4"

    # Intent: Request Email Copy of Report
    elif any(word in text for word in ["email", "mail"]):
        return "5"

    # Intent: Exit the system
    elif any(word in text for word in ["exit", "quit"]):
        return "9"

    # If no intent is recognized
    return None


# ---------------------------------------------------------
# Conversational Endpoint (Milestone 3)
# This endpoint allows users to interact with the IVR
# system using natural language instead of pressing digits.
# The detected intent is converted into the corresponding
# IVR menu option and routed to the existing menu handler.
# ---------------------------------------------------------

@app.post("/converse")
def converse(session_id: str, user_text: str):

    # Detect intent from natural language input
    digit = detect_intent(user_text)
    # If patient ID is detected from natural language
    if digit and digit.startswith("patient_id:"):
        patient_id = digit.split(":")[1]

        input_data = MenuInputRequest(
            session_id=session_id,
            user_input=patient_id
        )

        return handle_menu(input_data)

    # If intent cannot be determined
    if digit is None:
        return {
            "message": "Sorry, I didn't understand that. You can ask about lab report status, lab timings, support, sample collection, or email report."
        }

    # Create the same request structure used by the menu system
    input_data = MenuInputRequest(
        session_id=session_id,
        user_input=digit
    )

    # Route to the existing IVR menu handler
    return handle_menu(input_data)
