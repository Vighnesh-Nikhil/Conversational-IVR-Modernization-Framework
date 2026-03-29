# Conversational IVR Modernization Framework

## Project Overview
This project focuses on modernizing a traditional IVR (Interactive Voice Response) system by integrating conversational AI capabilities. The system replaces keypad-based navigation with natural language interaction using text and voice.

The application is built using FastAPI for the backend and a lightweight web interface for user interaction.

---

## Features

- Traditional IVR menu system (Milestone 2)
- Conversational AI interface using natural language (Milestone 3)
- Voice input using Speech Recognition
- Voice output using Text-to-Speech
- Session management for multi-step conversations
- Real-time interaction through web interface
- Deployed backend API

---

## Milestones

### Milestone 1: Requirement Analysis
- Studied traditional IVR systems
- Identified limitations of keypad-based interaction
- Designed system architecture

### Milestone 2: IVR Backend Development
- Built IVR system using FastAPI
- Implemented menu-based navigation
- Added session handling and APIs

### Milestone 3: Conversational AI Integration
- Implemented intent detection using natural language
- Mapped user input to IVR menu options
- Enabled conversational interaction
- Added entity extraction (Patient ID)

### Milestone 4: Testing and Deployment
- Performed unit testing using PyTest
- Verified conversational flow and system responses
- Deployed application using Render
- Added monitoring and validation

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- HTML, JavaScript
- SpeechRecognition API
- Web Speech API

---

## Deployed Application

Backend API:
https://conversational-ivr-modernization-pcpz.onrender.com/

---

## How to Run Locally

1. Clone the repository
2. Navigate to project folder
3. Create virtual environment
4. Install dependencies:

pip install -r requirements.txt

5. Run server:

uvicorn backend_ivr:app --reload

6. Open index.html in browser

---

## Project Structure

backend_ivr.py – Main backend logic  
milestone3_conversational.py – Conversational logic (merged into backend)  
tests/ – Unit tests  
requirements.txt – Dependencies  
README.md – Project documentation  
LICENSE – MIT License  

---

## License

This project is licensed under the MIT License.