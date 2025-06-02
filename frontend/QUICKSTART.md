# 🚀 VerifID Frontend - Quick Start Guide

Get the VerifID frontend up and running in 5 minutes!

## ⚡ Super Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
cd frontend
npm run setup
```

### Option 2: Manual Setup
```bash
cd frontend
npm install
npm run dev
```

## 📋 Prerequisites Checklist

- [ ] **Node.js 16+** installed ([Download here](https://nodejs.org/))
- [ ] **Modern browser** (Chrome, Firefox, Safari, Edge)
- [ ] **Webcam access** enabled
- [ ] **Flask backend** running on port 5001

## 🎯 Quick Test

1. **Start the app**: `npm run dev`
2. **Open browser**: Go to `http://localhost:5173`
3. **Test registration**: Create a new account
4. **Test ID verification**: Upload an ID card image
5. **Test face verification**: Allow webcam access and follow instructions

## 🔧 Common Quick Fixes

### "Cannot connect to backend"
```bash
# Check if backend is running
curl http://localhost:5001
# If not, start the Flask backend first
```

### "Camera access denied"
- Click the camera icon in browser address bar
- Allow camera permissions
- Refresh the page

### "Dependencies installation failed"
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### "Port 5173 already in use"
```bash
# Kill process using the port
npx kill-port 5173
# Or use a different port
npm run dev -- --port 3000
```

## 📱 Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 60+     | ✅ Recommended |
| Firefox | 55+     | ✅ Supported |
| Safari  | 11+     | ✅ Supported |
| Edge    | 79+     | ✅ Supported |

## 🚨 Troubleshooting

### Issue: White screen after starting
**Solution**: Check browser console for errors, ensure all dependencies are installed

### Issue: Webcam not working
**Solution**: 
1. Use HTTPS in production
2. Check camera permissions
3. Close other apps using camera

### Issue: Socket connection failed
**Solution**: 
1. Ensure backend is running
2. Check firewall settings
3. Try refreshing the page

### Issue: Build fails
**Solution**:
```bash
# Update Node.js to latest LTS
# Clear caches
rm -rf node_modules/.vite dist
npm install
npm run build
```

## 📞 Need Help?

1. **Check the full README.md** for detailed instructions
2. **Look at browser console** for error messages
3. **Verify backend is running** on `http://localhost:5001`
4. **Check camera permissions** in browser settings

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Frontend loads at `http://localhost:5173`
- ✅ Registration form works
- ✅ ID card upload processes successfully
- ✅ Webcam activates for face verification
- ✅ Real-time face detection works

## 📚 Next Steps

Once everything is running:
1. **Explore the features** - Try the full verification flow
2. **Check the code** - Look at the React components
3. **Customize styling** - Modify SCSS files in `src/styles/`
4. **Add features** - Extend the application as needed

---

**Happy coding! 🚀**

For detailed documentation, see [README.md](./README.md)
