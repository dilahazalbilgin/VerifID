# VerifID - AI-Powered Identity Verification System

<div align="center">
  <img src="frontend/src/assets/logo.png" alt="VerifID Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-19.0.0-blue.svg)](https://reactjs.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
</div>

## 🚀 Overview

VerifID is a cutting-edge identity verification system that combines AI-powered document processing with real-time face liveness detection. The system provides secure, accurate, and user-friendly identity verification for modern applications.

### ✨ Key Features

- **🔍 AI-Powered OCR**: Advanced text extraction from ID documents using Tesseract OCR
- **👤 Face Recognition**: Real-time face detection and matching using face_recognition library
- **🎭 Liveness Detection**: Anti-spoofing protection with dynamic head movement verification
- **📱 Real-time Processing**: WebSocket-based live video processing
- **🔒 Secure Storage**: Encrypted user data and secure face encoding storage
- **📊 User Dashboard**: Comprehensive profile management and verification status
- **🌐 Modern UI**: Responsive React frontend with SCSS styling

## 🏗️ Architecture

```
VerifID/
├── frontend/          # React.js frontend application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── styles/        # SCSS stylesheets
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
├── backend/           # Node.js backend (Authentication & User Management)
│   ├── server.js         # Main Node.js server
│   ├── controllers/      # Route controllers
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   └── middleware/      # Authentication middleware
├── flask_backend/     # Flask backend (Verification & AI Processing)
│   ├── app.py            # Main Flask application
│   ├── liveness_service.py # Face verification logic
│   ├── ocr_utils.py      # Document processing
│   └── requirements.txt   # Python dependencies
├── face_info/         # Stored face encodings
└── uploads/           # Temporary file storage
```

## 🛠️ Technology Stack

### Frontend
- **React 19.0.0** - Modern UI framework
- **React Router DOM 7.5.3** - Client-side routing
- **Socket.IO Client 4.8.1** - Real-time communication
- **Sass 1.87.0** - CSS preprocessing
- **Vite** - Fast build tool and dev server

### Backend (Dual Server Architecture)

#### Node.js Backend (Authentication & User Management)
- **Node.js** - JavaScript runtime for server-side development
- **Express.js** - Web application framework
- **MongoDB/Database** - User data storage
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing and security

#### Flask Backend (AI & Verification Processing)
- **Flask 3.0.0** - Python web framework
- **Flask-SocketIO** - WebSocket support for real-time communication
- **OpenCV** - Computer vision processing
- **face_recognition** - Face detection and recognition
- **Tesseract OCR** - Text extraction from documents
- **Pillow** - Image processing
- **NumPy** - Numerical computations

## 📋 Prerequisites

Before setting up VerifID, ensure you have the following installed:

- **Node.js** (v16 or higher) - For the authentication backend
- **Python** (3.8 or higher) - For the verification backend
- **MongoDB** (or your preferred database) - For user data storage
- **Tesseract OCR** (for document text extraction)
- **Git** (for cloning the repository)

### Installing Tesseract OCR

#### Windows
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or using chocolatey:
choco install tesseract
```

#### macOS
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/VerifID.git
cd VerifID
```

### 2. Backend Setup (Dual Server)

#### Node.js Backend (Authentication Server)
```bash
# Navigate to Node.js backend directory
cd backend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with your database connection and JWT secret

# Start the Node.js server
npm start
```

The Node.js backend will start on `http://localhost:3000`

#### Flask Backend (Verification Server)
```bash
# Navigate to Flask backend directory
cd flask_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The Flask backend will start on `http://localhost:5001`

### 3. Frontend Setup
```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:5173`

## 📖 How It Works

VerifID uses a **dual-server architecture** to separate concerns and optimize performance:

### 🔐 Node.js Backend (Authentication & User Management)
- **User Registration & Login**: Secure account creation and authentication
- **JWT Token Management**: Session handling and authorization
- **User Profile Management**: Personal information and account settings
- **Database Operations**: User data storage and retrieval
- **API Gateway**: Routes requests between frontend and verification server

### 🤖 Flask Backend (AI & Verification Processing)
- **ID Document Processing**: AI-powered OCR text extraction from documents
- **Face Detection**: Isolates and processes face photos from ID documents
- **Liveness Detection**: Real-time webcam verification with movement commands
- **Face Matching**: Compares live face with stored ID document photo
- **Anti-Spoofing**: Advanced protection against photo/video attacks

### 🔄 Complete Verification Flow
1. **Authentication**: User logs in through Node.js backend
2. **Document Upload**: ID document sent to Flask backend for processing
3. **OCR Processing**: Text extraction and face isolation from document
4. **Live Verification**: Real-time face liveness detection via WebSocket
5. **Face Matching**: Comparison between live face and document photo
6. **Results**: Verification status returned to user through Node.js backend

## 🔧 Configuration

### Environment Variables

#### Node.js Backend Configuration
Create a `.env` file in the `backend/` directory:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/verifid
# or your MongoDB connection string

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRE=7d

# Flask Backend URL
FLASK_BACKEND_URL=http://localhost:5001
```

#### Flask Backend Configuration
Create a `.env` file in the `flask_backend/` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# File Upload Settings
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE=0.55
LIVENESS_TIMEOUT=10

# OCR Settings
TESSERACT_PATH=/usr/bin/tesseract  # Adjust for your system

# Node.js Backend URL
NODE_BACKEND_URL=http://localhost:3000
```

### Frontend Configuration
Update `frontend/src/config.js`:

```javascript
export const AUTH_API_BASE_URL = 'http://localhost:3000';  // Node.js backend
export const VERIFY_API_BASE_URL = 'http://localhost:5001'; // Flask backend
export const SOCKET_URL = 'http://localhost:5001';          // WebSocket for verification
```

## 🧪 Testing

### Backend Tests
```bash
cd flask_backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Production Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app:app
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files (example with nginx)
# Copy dist/ contents to your web server
```

## 🔒 Security Features

- **Encrypted Data Storage**: All sensitive data is encrypted at rest
- **Secure Face Encodings**: Face data stored as mathematical encodings, not images
- **Anti-Spoofing**: Liveness detection prevents photo/video attacks
- **Session Management**: Secure user authentication and session handling
- **Input Validation**: Comprehensive validation of all user inputs

## 🤝 Contributing

We welcome contributions to VerifID! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/YOUR_USERNAME/VerifID/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers directly

## 🐛 Troubleshooting

### Common Issues

#### "Could not process reference face" Error
- Ensure face images are clear and well-lit
- Check that face_info directory exists and contains user face images
- Verify face_recognition library is properly installed

#### Webcam Access Issues
- Grant camera permissions in your browser
- Ensure no other applications are using the camera
- Try refreshing the page or restarting the browser

#### OCR Not Working
- Verify Tesseract is installed and in PATH
- Check document image quality and lighting
- Ensure supported document formats (JPG, PNG)

#### Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js and Python versions match requirements
- Verify all dependencies are installed correctly

### Performance Optimization

- **Face Detection**: Adjust `face_detection_threshold` for better accuracy
- **Video Processing**: Modify frame processing rate in liveness detection
- **File Upload**: Optimize image compression before upload
- **Database**: Consider using a proper database for production

## 📊 API Documentation

### Node.js Backend API (Authentication)
```
POST /api/auth/register    # User registration
POST /api/auth/login       # User login
POST /api/auth/logout      # User logout
GET  /api/auth/profile     # Get user profile
PUT  /api/auth/profile     # Update user profile
GET  /api/users/me         # Get current user info
```

### Flask Backend API (Verification)
```
POST /api/verify/id                    # Upload ID document
POST /api/verify/face/initialize       # Start face verification
GET  /api/verify/face/check/{id}       # Check verification status
GET  /api/uploads/{filename}           # Get uploaded files
```

### WebSocket Events
```
start_liveness_check    # Initialize liveness detection
liveness_frame         # Send video frame for processing
liveness_instruction   # Receive movement instructions
liveness_feedback      # Receive real-time feedback
liveness_result        # Receive final verification result
liveness_error         # Receive error messages
```

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with core functionality
- ID document verification with OCR
- Face liveness detection
- User authentication and profiles
- Real-time WebSocket communication

### Planned Features
- [ ] Multi-language OCR support
- [ ] Mobile app development
- [ ] Advanced anti-spoofing techniques
- [ ] Integration with external verification services
- [ ] Audit logging and compliance features

## 🙏 Acknowledgments

- [OpenCV](https://opencv.org/) for computer vision capabilities
- [face_recognition](https://github.com/ageitgey/face_recognition) for face detection
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction
- [React](https://reactjs.org/) for the frontend framework
- [Flask](https://flask.palletsprojects.com/) for the backend framework
- [Socket.IO](https://socket.io/) for real-time communication

---

<div align="center">
  <p>Made with ❤️ by the VerifID Team</p>
  <p>
    <a href="https://github.com/YOUR_USERNAME/VerifID">⭐ Star this project</a> •
    <a href="https://github.com/YOUR_USERNAME/VerifID/issues">🐛 Report Bug</a> •
    <a href="https://github.com/YOUR_USERNAME/VerifID/issues">💡 Request Feature</a>
  </p>
</div>
