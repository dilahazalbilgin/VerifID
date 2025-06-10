import User from '../models/User.js';
import generateToken from '../utils/generateToken.js';

// @desc    Register a new user
// @route   POST /api/users
// @access  Public
export const registerUser = async (req, res) => {
  try {
    const { 
      firstName, 
      lastName, 
      email, 
      password, 
      idCardNumber, 
      serialNumber, 
      birthDate, 
      gender 
    } = req.body;

    // Check if user already exists by email
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'User with this email already exists' });
    }

    // Check if ID card number already exists
    const idCardExists = await User.findOne({ idCardNumber });
    if (idCardExists) {
      return res.status(400).json({ message: 'User with this ID card number already exists' });
    }

    // Create new user
    const user = await User.create({
      firstName,
      lastName,
      email,
      password,
      idCardNumber,
      serialNumber,
      birthDate,
      gender
    });

    if (user) {
      res.status(201).json({
        _id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        idCardNumber: user.idCardNumber,
        serialNumber: user.serialNumber,
        birthDate: user.birthDate,
        gender: user.gender,
        isVerified: user.isVerified,
        requestId: user.requestId,
        token: generateToken(user._id)
      });
    } else {
      res.status(400).json({ message: 'Invalid user data' });
    }
  } catch (error) {
    console.error('Registration error:', error);

    // Handle MongoDB duplicate key errors
    if (error.code === 11000) {
      const field = Object.keys(error.keyPattern)[0];
      let message = 'Duplicate entry detected';

      if (field === 'email') {
        message = 'User with this email already exists';
      } else if (field === 'idCardNumber') {
        message = 'User with this ID card number already exists';
      }

      return res.status(400).json({ message });
    }

    // Handle validation errors
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      return res.status(400).json({
        message: 'Validation failed',
        errors: messages
      });
    }

    // Generic server error
    res.status(500).json({
      message: 'Server error occurred during registration',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};

// @desc    Auth user & get token
// @route   POST /api/users/login
// @access  Public
export const loginUser = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user by email
    const user = await User.findOne({ email });

    // Check if user exists and password matches
    if (user && (await user.matchPassword(password))) {
      res.json({
        _id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        idCardNumber: user.idCardNumber,
        serialNumber: user.serialNumber,
        birthDate: user.birthDate,
        gender: user.gender,
        isVerified: user.isVerified,
        requestId: user.requestId,
        token: generateToken(user._id)
      });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    res.status(500).json({ 
      message: 'Server error', 
      error: error.message 
    });
  }
};

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
export const updateUserProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (user) {
      // Update existing fields
      user.firstName = req.body.firstName || user.firstName;
      user.lastName = req.body.lastName || user.lastName;
      user.email = req.body.email || user.email;
      user.idCardNumber = req.body.idCardNumber || user.idCardNumber;
      user.serialNumber = req.body.serialNumber || user.serialNumber;
      user.birthDate = req.body.birthDate || user.birthDate;
      user.gender = req.body.gender || user.gender;
      user.isVerified = req.body.isVerified !== undefined ? req.body.isVerified : user.isVerified;
      
      // Add face image if provided
      if (req.body.idCardFace) {
        user.idCardFace = req.body.idCardFace;
      }
      
      if (req.body.password) {
        user.password = req.body.password;
      }
      
      const updatedUser = await user.save();
      
      res.json({
        _id: updatedUser._id,
        firstName: updatedUser.firstName,
        lastName: updatedUser.lastName,
        email: updatedUser.email,
        idCardNumber: updatedUser.idCardNumber,
        serialNumber: updatedUser.serialNumber,
        birthDate: updatedUser.birthDate,
        gender: updatedUser.gender,
        isVerified: updatedUser.isVerified,
        requestId: updatedUser.requestId,
        idCardFace: updatedUser.idCardFace,
        token: req.token || generateToken(updatedUser._id)
      });
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  } catch (error) {
    console.error('Profile update error:', error);

    // Handle MongoDB duplicate key errors
    if (error.code === 11000) {
      const field = Object.keys(error.keyPattern)[0];
      let message = 'Duplicate entry detected';

      if (field === 'email') {
        message = 'User with this email already exists';
      } else if (field === 'idCardNumber') {
        message = 'User with this ID card number already exists';
      }

      return res.status(400).json({ message });
    }

    // Handle validation errors
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message);
      return res.status(400).json({
        message: 'Validation failed',
        errors: messages
      });
    }

    // Generic server error
    res.status(500).json({
      message: 'Server error occurred during profile update',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};





