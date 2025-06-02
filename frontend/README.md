# VerifID Frontend

A React-based frontend application for identity verification using ID card scanning and face verification.

## 🚀 Features

- **User Authentication**: Registration and login system
- **ID Card Verification**: Upload and verify Turkish ID cards with OCR
- **Face Verification**: Real-time face liveness detection and matching
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Communication**: WebSocket integration for live face verification

## 📋 Prerequisites

Before setting up the frontend, make sure you have:

- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Modern web browser** with webcam support
- **Flask Backend** running on `http://localhost:5001`

## 🛠️ Installation & Setup

### 1. Clone or Download the Project
```bash
# If cloning from git
git clone <repository-url>
cd VerifIDcodes/frontend

# Or if you downloaded the files
cd path/to/VerifIDcodes/frontend
```

### 2. Install Dependencies
```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### 3. Start the Development Server
```bash
# Using npm
npm run dev

# Or using yarn
yarn dev
```

The application will start on `http://localhost:5173` by default.

## 📦 Dependencies

### Core Dependencies
- **React 19.0.0**: UI framework
- **React Router DOM 7.5.3**: Client-side routing
- **Socket.IO Client 4.8.1**: Real-time communication with backend
- **Sass 1.87.0**: CSS preprocessing

### Development Dependencies
- **Vite 6.3.1**: Build tool and dev server
- **ESLint**: Code linting
- **@vitejs/plugin-react**: React support for Vite

## 🏗️ Project Structure

```
frontend/
├── public/
│   └── vite.svg                 # Favicon
├── src/
│   ├── assets/                  # Images and static files
│   │   ├── login-image.jpg
│   │   ├── logo.png
│   │   └── verification-image.jpg
│   ├── components/              # Reusable components
│   │   ├── Navbar.jsx
│   │   └── ProtectedRoute.jsx
│   ├── context/                 # React context providers
│   │   └── AuthContext.jsx
│   ├── pages/                   # Page components
│   │   ├── homePage/
│   │   │   └── Home.jsx
│   │   ├── loginPage/
│   │   │   └── Login.jsx
│   │   ├── profilePage/
│   │   │   └── Profile.jsx
│   │   ├── registerPage/
│   │   │   └── Register.jsx
│   │   ├── verificationPage/
│   │   │   ├── IDCardVerification.jsx
│   │   │   └── VideoVerification.jsx
│   │   └── NotFound.jsx
│   ├── styles/                  # SCSS stylesheets
│   │   ├── global.css
│   │   ├── HomePage.module.scss
│   │   ├── LoginPage.module.scss
│   │   ├── Navbar.module.scss
│   │   ├── NotFound.module.scss
│   │   ├── ProfilePage.module.scss
│   │   ├── RegisterPage.module.scss
│   │   └── VerificationPage.module.scss
│   ├── App.jsx                  # Main app component
│   └── main.jsx                 # Entry point
├── package.json                 # Dependencies and scripts
├── vite.config.js              # Vite configuration
└── README.md                   # This file
```

## ⚙️ Configuration

### Backend Connection
The frontend is configured to connect to the Flask backend at:
- **REST API**: `http://localhost:5001`
- **WebSocket**: `http://localhost:5001` (Socket.IO)

If your backend runs on a different port, update the URLs in:
- `src/context/AuthContext.jsx` (for authentication)
- `src/pages/verificationPage/IDCardVerification.jsx` (for ID verification)
- `src/pages/verificationPage/VideoVerification.jsx` (for face verification)

### Environment Variables (Optional)
You can create a `.env` file in the frontend directory:
```env
VITE_API_BASE_URL=http://localhost:5001
VITE_SOCKET_URL=http://localhost:5001
```

## 🎯 Usage

### 1. User Registration
- Navigate to `/register`
- Fill in personal information (name, surname, ID number, etc.)
- Create account with email and password

### 2. User Login
- Navigate to `/login`
- Enter email and password
- Redirected to verification or profile based on verification status

### 3. ID Card Verification
- Upload a clear photo of Turkish ID card
- System extracts information using OCR
- Matches extracted data with user profile
- Face is extracted and saved for face verification

### 4. Face Verification
- Real-time webcam access required
- Follow on-screen instructions for head movements
- System verifies face matches ID card photo
- Completes verification process

## 📱 Browser Requirements

### Supported Browsers
- **Chrome** 60+ (recommended)
- **Firefox** 55+
- **Safari** 11+
- **Edge** 79+

### Required Permissions
- **Camera access** for face verification
- **JavaScript enabled**
- **WebSocket support**

## 🔧 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run ESLint
npm run lint
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Dependencies Installation Fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 2. Backend Connection Issues
- Ensure Flask backend is running on `http://localhost:5001`
- Check CORS settings in backend
- Verify firewall/antivirus isn't blocking connections

#### 3. Webcam Access Denied
- Enable camera permissions in browser
- Use HTTPS in production (required for camera access)
- Check if another application is using the camera

#### 4. Socket.IO Connection Problems
- Check browser console for WebSocket errors
- Ensure backend has Socket.IO properly configured
- Try refreshing the page

#### 5. Build Issues
```bash
# Update Node.js to latest LTS version
# Clear Vite cache
rm -rf node_modules/.vite

# Reinstall dependencies
npm install
```

### Development Tips

#### Hot Reload Not Working
- Check if files are being watched correctly
- Restart the dev server: `npm run dev`
- Clear browser cache

#### Styling Issues
- SCSS files use CSS modules
- Import styles as: `import styles from './Component.module.scss'`
- Use: `className={styles.className}`

## 🔒 Security Notes

- Never commit sensitive data to version control
- Use environment variables for API endpoints in production
- Ensure HTTPS in production for webcam access
- Validate all user inputs on both frontend and backend

## 🚀 Production Deployment

### Build for Production
```bash
npm run build
```

### Deploy Built Files
The `dist/` folder contains the production build:
- Upload to web server
- Configure server to serve `index.html` for all routes (SPA)
- Ensure HTTPS for webcam functionality

### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## 📞 Support

If you encounter issues:
1. Check the browser console for errors
2. Verify backend is running and accessible
3. Ensure all dependencies are installed correctly
4. Check camera and microphone permissions

## 🔄 Updates

To update dependencies:
```bash
# Check for outdated packages
npm outdated

# Update all packages
npm update

# Update specific package
npm install package-name@latest
```
