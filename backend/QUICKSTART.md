# 🚀 VerifID Backend - Quick Start Guide

Get the VerifID Node.js backend up and running in 5 minutes!

## ⚡ Super Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
cd backend
npm run setup
```

### Option 2: Manual Setup
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your MongoDB URI
npm run dev
```

## 📋 Prerequisites Checklist

- [ ] **Node.js 16+** installed ([Download here](https://nodejs.org/))
- [ ] **MongoDB** running (local or Atlas account)
- [ ] **Git** for cloning (optional)

## 🎯 Quick Test

1. **Start the server**: `npm run dev`
2. **Test API**: `curl http://localhost:5000`
3. **Register user**: Use Postman or curl to test `/api/users/register`
4. **Login user**: Test `/api/users/login`

## 🗄️ Database Setup Options

### Option A: Local MongoDB
```bash
# Install MongoDB Community Server
# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS

# Use default connection in .env:
MONGODB_URI=mongodb://localhost:27017/verifid
```

### Option B: MongoDB Atlas (Cloud)
```bash
# 1. Create account at https://www.mongodb.com/atlas
# 2. Create cluster
# 3. Get connection string
# 4. Update .env:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/verifid
```

## 🔧 Common Quick Fixes

### "MongoDB connection failed"
```bash
# Check if MongoDB is running
sudo systemctl status mongod  # Linux
brew services list | grep mongo  # macOS

# Or use MongoDB Atlas (cloud option)
```

### "Port 5000 already in use"
```bash
# Find and kill process
lsof -i :5000
kill -9 <PID>

# Or change port in .env
PORT=5001
```

### "JWT_SECRET is required"
```bash
# Generate a secure JWT secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Add to .env file
```

### "Dependencies installation failed"
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📱 API Testing

### Quick Test Commands

#### Test Server
```bash
curl http://localhost:5000
```

#### Register User
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

## 🚨 Troubleshooting

### Issue: "Cannot find module"
**Solution**: Run `npm install` to install dependencies

### Issue: "MongoNetworkError"
**Solution**: 
1. Check MongoDB is running: `sudo systemctl status mongod`
2. Verify MONGODB_URI in .env
3. For Atlas: Check IP whitelist and credentials

### Issue: "CORS error"
**Solution**: 
1. Check FRONTEND_URL in .env
2. Ensure frontend is running on correct port
3. Verify CORS configuration in server.js

### Issue: "JWT malformed"
**Solution**: 
1. Check JWT_SECRET is set in .env
2. Ensure token is properly formatted
3. Verify Authorization header format

## 📊 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 5000 | Server port |
| `MONGODB_URI` | Yes | - | MongoDB connection string |
| `JWT_SECRET` | Yes | - | JWT signing secret |
| `JWT_EXPIRES_IN` | No | 30d | Token expiration |
| `FRONTEND_URL` | No | http://localhost:5173 | CORS origin |

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Server starts without errors
- ✅ MongoDB connection successful
- ✅ API endpoints respond correctly
- ✅ User registration/login works
- ✅ JWT tokens are generated

## 📚 Next Steps

Once everything is running:
1. **Test all endpoints** - Use Postman or curl
2. **Connect frontend** - Ensure frontend can communicate
3. **Check database** - Verify users are being saved
4. **Review security** - Update JWT secrets for production

## 🔗 Integration with Frontend

Make sure your frontend is configured to connect to:
- **API Base URL**: `http://localhost:5000`
- **Socket URL**: Not applicable (this backend doesn't use sockets)
- **CORS**: Backend allows requests from `http://localhost:5173`

---

**Happy coding! 🚀**

For detailed documentation, see [README.md](./README.md)
