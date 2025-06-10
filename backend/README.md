# VerifID Node.js Backend

A Node.js/Express backend API for user authentication and management in the VerifID identity verification system.

## 🚀 Features

- **User Authentication**: Registration and login with JWT tokens
- **Password Security**: Bcrypt hashing for secure password storage
- **Third-Party Verification**: Request ID system for external app verification
- **MongoDB Integration**: User data storage with Mongoose ODM
- **CORS Support**: Cross-origin requests enabled for frontend
- **Environment Configuration**: Secure environment variable management
- **RESTful API**: Clean API endpoints for user operations

## 📋 Prerequisites

Before setting up the backend, make sure you have:

- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **MongoDB** (local installation or MongoDB Atlas account)
- **Git** (for cloning the repository)

## 🛠️ Installation & Setup

### 1. Clone or Download the Project
```bash
# If cloning from git
git clone <repository-url>
cd VerifIDcodes/backend

# Or if you downloaded the files
cd path/to/VerifIDcodes/backend
```

### 2. Install Dependencies
```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### 3. Environment Configuration
Create a `.env` file in the backend directory:
```bash
# Copy the example environment file
cp .env.example .env

# Or create manually
touch .env
```

Add the following environment variables to `.env`:
```env
# Server Configuration
PORT=5000
NODE_ENV=development

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/verifid
# For MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/verifid

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_IN=30d

# CORS Configuration (optional)
FRONTEND_URL=http://localhost:5173
```

### 4. Database Setup

#### Option A: Local MongoDB
1. **Install MongoDB**: [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
2. **Start MongoDB service**:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS (with Homebrew)
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

#### Option B: MongoDB Atlas (Cloud)
1. **Create account**: Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create cluster**: Follow the setup wizard
3. **Get connection string**: Replace `MONGODB_URI` in `.env`
4. **Whitelist IP**: Add your IP address to allowed connections

### 5. Start the Server
```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

The server will start on `http://localhost:5000` by default.

## 📦 Dependencies

### Core Dependencies
- **express**: Web framework for Node.js
- **mongoose**: MongoDB object modeling
- **bcrypt**: Password hashing
- **jsonwebtoken**: JWT token generation and verification
- **cors**: Cross-origin resource sharing
- **dotenv**: Environment variable management

### Development Dependencies
- **nodemon**: Auto-restart server during development

## 🏗️ Project Structure

```
backend/
├── config/
│   └── db.js                    # MongoDB connection configuration
├── controllers/
│   └── userController.js        # User-related business logic
├── middleware/
│   └── authMiddleware.js        # JWT authentication middleware
├── models/
│   └── User.js                  # User data model (Mongoose schema)
├── routes/
│   └── userRoutes.js           # User API routes
├── utils/
│   └── generateToken.js        # JWT token utility functions
├── node_modules/               # Dependencies (auto-generated)
├── .env                        # Environment variables (create this)
├── .env.example               # Environment template (create this)
├── package.json               # Dependencies and scripts
├── package-lock.json          # Dependency lock file
├── server.js                  # Main application entry point
└── README.md                  # This file
```

## 🔌 API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/users/register
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123",
  "idCardNumber": "12345678901",
  "gender": "Male",
  "birthDate": "1990-01-01",
  "serialNumber": "A12B34567"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": "user_id",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "isVerified": false
  },
  "token": "jwt_token_here"
}
```

#### Login User
```http
POST /api/users/login
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "user_id",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "isVerified": false
  },
  "token": "jwt_token_here"
}
```

#### Get User Profile
```http
GET /api/users/profile
Authorization: Bearer jwt_token_here
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_id",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "isVerified": false,
    "idCardNumber": "12345678901",
    "gender": "Male",
    "birthDate": "1990-01-01"
  }
}
```

#### Update User Profile
```http
PUT /api/users/profile
Authorization: Bearer jwt_token_here
Content-Type: application/json

{
  "isVerified": true
}
```

### Third-Party Verification Endpoints

#### Generate Request ID (Protected)
```http
POST /api/verification/generate-request-id
Authorization: Bearer jwt_token_here
```

**Response:**
```json
{
  "success": true,
  "message": "Request ID generated successfully",
  "requestId": "req_lm2n3o4p_abc123def456",
  "user": {
    "id": "user_id",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "isVerified": true
  }
}
```

#### Verify User by Request ID (Public)
```http
GET /api/verification/verify/{requestId}
```

**Response:**
```json
{
  "success": true,
  "message": "User verification status retrieved successfully",
  "verified": true,
  "requestId": "req_lm2n3o4p_abc123def456",
  "user": {
    "id": "user_id",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "idCardNumber": "12345678901",
    "isVerified": true,
    "verifiedAt": "2024-01-15T10:30:00.000Z"
  },
  "timestamp": "2024-01-15T14:25:30.123Z"
}
```

#### Get My Request ID (Protected)
```http
GET /api/verification/my-request-id
Authorization: Bearer jwt_token_here
```

#### Revoke Request ID (Protected)
```http
DELETE /api/verification/revoke-request-id
Authorization: Bearer jwt_token_here
```

> 📖 **For detailed third-party verification API documentation, see [VERIFICATION_API.md](./VERIFICATION_API.md)**

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Server port | 5000 | No |
| `NODE_ENV` | Environment mode | development | No |
| `MONGODB_URI` | MongoDB connection string | - | Yes |
| `JWT_SECRET` | JWT signing secret | - | Yes |
| `JWT_EXPIRES_IN` | JWT expiration time | 30d | No |
| `FRONTEND_URL` | Frontend URL for CORS | http://localhost:5173 | No |

### MongoDB Connection Strings

#### Local MongoDB
```env
MONGODB_URI=mongodb://localhost:27017/verifid
```

#### MongoDB Atlas
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/verifid?retryWrites=true&w=majority
```

#### MongoDB with Authentication
```env
MONGODB_URI=mongodb://username:password@localhost:27017/verifid
```

## 🔧 Available Scripts

```bash
# Start development server (with auto-restart)
npm run dev

# Start production server
npm start

# Run tests (when implemented)
npm test
```

## 🧪 Testing the API

### Using curl

#### Test Server Status
```bash
curl http://localhost:5000
```

#### Register a New User
```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "password": "password123",
    "idCardNumber": "12345678901",
    "gender": "Male",
    "birthDate": "1990-01-01"
  }'
```

#### Login User
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Get User Profile (replace TOKEN with actual JWT)
```bash
curl -X GET http://localhost:5000/api/users/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Using Postman

1. **Import Collection**: Create a new Postman collection
2. **Set Base URL**: `http://localhost:5000`
3. **Add Requests**: Create requests for each endpoint
4. **Set Headers**: Add `Content-Type: application/json`
5. **Add Authorization**: Use Bearer Token for protected routes

## 🚨 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```bash
Error: MongoNetworkError: failed to connect to server
```

**Solutions:**
- Ensure MongoDB is running: `sudo systemctl status mongod`
- Check connection string in `.env`
- Verify MongoDB port (default: 27017)
- For Atlas: Check IP whitelist and credentials

#### 2. JWT Secret Missing
```bash
Error: JWT_SECRET is required
```

**Solution:**
- Add `JWT_SECRET` to your `.env` file
- Use a strong, random string (at least 32 characters)

#### 3. Port Already in Use
```bash
Error: listen EADDRINUSE: address already in use :::5000
```

**Solutions:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=5001 npm run dev
```

#### 4. CORS Issues
```bash
Access to fetch at 'http://localhost:5000' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:**
- Ensure CORS is properly configured in `server.js`
- Check `FRONTEND_URL` in `.env`

#### 5. Dependencies Installation Failed
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Development Tips

#### Enable Debug Logging
```bash
DEBUG=* npm run dev
```

#### Check Environment Variables
```bash
node -e "console.log(process.env)"
```

#### Validate MongoDB Connection
```bash
# Connect to MongoDB shell
mongosh

# Or for older versions
mongo

# List databases
show dbs

# Use your database
use verifid

# List collections
show collections
```

## 🚀 Production Deployment

### Environment Setup
```env
NODE_ENV=production
PORT=5000
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/verifid
JWT_SECRET=your-super-secure-production-jwt-secret
JWT_EXPIRES_IN=7d
FRONTEND_URL=https://your-frontend-domain.com
```

### Deployment Platforms

#### Heroku
```bash
# Install Heroku CLI
npm install -g heroku

# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set MONGODB_URI=your-mongodb-uri
heroku config:set JWT_SECRET=your-jwt-secret

# Deploy
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### DigitalOcean/VPS
```bash
# Install PM2 for process management
npm install -g pm2

# Start application
pm2 start server.js --name "verifid-backend"

# Save PM2 configuration
pm2 save
pm2 startup
```



## 🔒 Security Best Practices

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique JWT secrets (32+ characters)
- Rotate JWT secrets regularly in production
- Use environment-specific configurations

### Password Security
- Passwords are hashed using bcrypt (already implemented)
- Minimum password requirements should be enforced on frontend
- Consider implementing password strength validation

### JWT Security
- Tokens expire after configured time (default: 30 days)
- Use HTTPS in production to prevent token interception
- Consider implementing token refresh mechanism
- Store tokens securely on client side

### Database Security
- Use MongoDB Atlas with IP whitelisting
- Enable authentication for local MongoDB
- Regular database backups
- Monitor for unusual access patterns

### CORS Configuration
- Configure specific origins instead of wildcard in production
- Limit allowed methods and headers
- Regular security audits

## 📞 Support & Maintenance

### Monitoring
```bash
# Check application logs
pm2 logs verifid-backend

# Monitor system resources
pm2 monit

# Check database status
mongosh --eval "db.adminCommand('serverStatus')"
```

### Backup Strategy
```bash
# Backup MongoDB database
mongodump --uri="mongodb://localhost:27017/verifid" --out=./backup

# Restore from backup
mongorestore --uri="mongodb://localhost:27017/verifid" ./backup/verifid
```

### Updates
```bash
# Check for outdated packages
npm outdated

# Update dependencies
npm update

# Security audit
npm audit
npm audit fix
```

## 📚 Additional Resources

- [Express.js Documentation](https://expressjs.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Mongoose Documentation](https://mongoosejs.com/)
- [JWT.io](https://jwt.io/) - JWT token debugger
- [bcrypt Documentation](https://www.npmjs.com/package/bcrypt)

---

**Happy coding! 🚀**

For questions or issues, please check the troubleshooting section or create an issue in the repository.
