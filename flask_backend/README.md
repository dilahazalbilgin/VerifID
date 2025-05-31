# VerifID Flask Backend

This Flask backend handles ID card text detection and webcam face verification for the VerifID application.

## Features

- ID card OCR processing
- Real-time face verification via WebSocket
- Step-by-step facial verification instructions

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install face_recognition_models:
   ```
   pip install git+https://github.com/ageitgey/face_recognition_models
   ```

4. Install Tesseract OCR:
   - **Windows**: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`
   
   Make sure to add Tesseract to your PATH.

5. Install dlib and face_recognition dependencies:
   - **Windows**: You may need Visual C++ build tools
   - **macOS**: `brew install cmake`
   - **Linux**: `sudo apt-get install -y build-essential cmake`

6. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

7. Run the server:
   ```
   python app.py
   ```

## API Endpoints

### ID Card Verification
- **POST** `/api/verify/id`
  - Accepts an ID card image and user data
  - Returns verification result with extracted information

### Face Verification
- **POST** `/api/verify/face/initialize`
  - Initializes a face verification session
  - Returns a verification ID for WebSocket communication

### Test Endpoints
- **GET** `/api/test/face-capture`
  - Captures a test image from webcam
  - Returns path to saved image

## WebSocket Events

### Server Events (emitted to client)
- `verification_connected`: Confirms connection
- `verification_instruction`: Sends next instruction to user
- `frame_processed`: Returns processed frame results
- `verification_complete`: Signals completion of verification

### Client Events (received from client)
- `start_verification`: Starts the verification process
- `face_frame`: Receives a frame from the client's webcam

## Integration with React Frontend

Connect to this backend from your React application using:
- Fetch API for REST endpoints
- Socket.IO client for WebSocket communication