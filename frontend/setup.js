#!/usr/bin/env node

/**
 * VerifID Frontend Setup Script
 * 
 * This script helps new users set up the frontend quickly by:
 * - Checking Node.js version
 * - Installing dependencies
 * - Creating environment file
 * - Providing next steps
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 VerifID Frontend Setup');
console.log('========================\n');

// Check Node.js version
function checkNodeVersion() {
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
    
    console.log(`📋 Checking Node.js version: ${nodeVersion}`);
    
    if (majorVersion < 16) {
        console.error('❌ Node.js version 16 or higher is required!');
        console.log('   Please update Node.js: https://nodejs.org/');
        process.exit(1);
    }
    
    console.log('✅ Node.js version is compatible\n');
}

// Check if package.json exists
function checkPackageJson() {
    if (!fs.existsSync('package.json')) {
        console.error('❌ package.json not found!');
        console.log('   Make sure you\'re in the frontend directory.');
        process.exit(1);
    }
    console.log('✅ package.json found\n');
}

// Install dependencies
function installDependencies() {
    console.log('📦 Installing dependencies...');
    
    try {
        // Check if npm is available
        execSync('npm --version', { stdio: 'ignore' });
        console.log('   Using npm to install packages...');
        execSync('npm install', { stdio: 'inherit' });
        console.log('✅ Dependencies installed successfully\n');
    } catch (error) {
        console.error('❌ Failed to install dependencies');
        console.log('   Please run: npm install');
        process.exit(1);
    }
}

// Create environment file
function createEnvFile() {
    const envPath = '.env';
    
    if (fs.existsSync(envPath)) {
        console.log('⚠️  .env file already exists, skipping creation\n');
        return;
    }
    
    const envContent = `# VerifID Frontend Environment Variables
# Backend API URL
VITE_API_BASE_URL=http://localhost:5001

# Socket.IO URL
VITE_SOCKET_URL=http://localhost:5001

# Development mode
VITE_NODE_ENV=development
`;
    
    try {
        fs.writeFileSync(envPath, envContent);
        console.log('✅ Created .env file with default settings\n');
    } catch (error) {
        console.log('⚠️  Could not create .env file (optional)\n');
    }
}

// Check backend connection
function checkBackendConnection() {
    console.log('🔍 Checking backend connection...');
    
    try {
        const http = require('http');
        const options = {
            hostname: 'localhost',
            port: 5001,
            path: '/',
            method: 'GET',
            timeout: 3000
        };
        
        const req = http.request(options, (res) => {
            if (res.statusCode === 200 || res.statusCode === 404) {
                console.log('✅ Backend is running on http://localhost:5001\n');
            } else {
                console.log('⚠️  Backend responded but may not be fully ready\n');
            }
        });
        
        req.on('error', () => {
            console.log('⚠️  Backend not running on http://localhost:5001');
            console.log('   Make sure to start the Flask backend first\n');
        });
        
        req.on('timeout', () => {
            console.log('⚠️  Backend connection timeout\n');
            req.destroy();
        });
        
        req.end();
    } catch (error) {
        console.log('⚠️  Could not check backend connection\n');
    }
}

// Display next steps
function displayNextSteps() {
    console.log('🎉 Setup Complete!');
    console.log('==================\n');
    
    console.log('📝 Next Steps:');
    console.log('1. Start the Flask backend (if not already running):');
    console.log('   cd ../flask_backend');
    console.log('   python app.py\n');
    
    console.log('2. Start the frontend development server:');
    console.log('   npm run dev\n');
    
    console.log('3. Open your browser and navigate to:');
    console.log('   http://localhost:5173\n');
    
    console.log('📚 Additional Commands:');
    console.log('   npm run build    - Build for production');
    console.log('   npm run preview  - Preview production build');
    console.log('   npm run lint     - Run ESLint\n');
    
    console.log('🔧 Troubleshooting:');
    console.log('   - Check README.md for detailed instructions');
    console.log('   - Ensure webcam permissions are enabled');
    console.log('   - Verify backend is running on port 5001\n');
    
    console.log('✨ Happy coding!');
}

// Main setup function
function main() {
    try {
        checkNodeVersion();
        checkPackageJson();
        installDependencies();
        createEnvFile();
        
        // Add a small delay before checking backend
        setTimeout(() => {
            checkBackendConnection();
            displayNextSteps();
        }, 1000);
        
    } catch (error) {
        console.error('❌ Setup failed:', error.message);
        process.exit(1);
    }
}

// Run setup
main();
