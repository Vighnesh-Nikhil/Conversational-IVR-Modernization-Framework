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
# ---------------------------------------------------------

import re
from backend_ivr import app, handle_menu, MenuInputRequest


# ---------------------------------------------------------
# Conversational AI Layer (Milestone 3)
# Detect user intent from natural language input
# ---------------------------------------------------------

def detect_intent(text: str):

    text = text.lower()

    # Detect patient ID numbers
    match = re.search(r"\b\d{5,}\b", text)
    if match:
        return "patient_id:" + match.group()

    # Lab Report Status
    if any(word in text for word in ["report", "lab report", "report status"]):
        return "1"

    # Lab Working Hours
    elif any(word in text for word in ["hour", "timing", "working hours"]):
        return "2"

    # Contact Support
    elif any(word in text for word in ["support", "help", "contact"]):
        return "3"

    # Sample Collection Information
    elif any(word in text for word in ["sample", "collection"]):
        return "4"

    # Request Email Copy of Report
    elif any(word in text for word in ["email", "mail"]):
        return "5"

    # Exit system
    elif any(word in text for word in ["exit", "quit"]):
        return "9"

    return None


# ---------------------------------------------------------
# Conversational Endpoint
# Users interact using natural language instead of digits
# ---------------------------------------------------------

@app.post("/converse")
def converse(session_id: str, user_text: str):

    digit = detect_intent(user_text)

    if digit is None:
        return {
            "message": "Sorry, I didn't understand that. You can ask about lab report status, lab timings, support, sample collection, or email report."
        }

    # If patient ID detected
    if digit.startswith("patient_id:"):

        patient_id = digit.split(":")[1]

        input_data = MenuInputRequest(
            session_id=session_id,
            user_input=patient_id
        )

        return handle_menu(input_data)

    # Normal menu mapping
    input_data = MenuInputRequest(
        session_id=session_id,
        user_input=digit
    )

    return handle_menu(input_data)
