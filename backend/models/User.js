import mongoose from 'mongoose';
import bcrypt from 'bcrypt';

const userSchema = new mongoose.Schema({
  firstName: {
    type: String,
    required: [true, 'First name is required']
  },
  lastName: {
    type: String,
    required: [true, 'Last name is required']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\S+@\S+\.\S+$/, 'Please enter a valid email']
  },
  password: {
    type: String,
    required: [true, 'Password is required'],
    minlength: 6
  },
  idCardNumber: {
    type: String,
    required: [true, 'ID card number is required'],
    unique: true
  },
  serialNumber: {
    type: String,
    required: [true, 'Serial number is required']
  },
  birthDate: {
    type: Date,
    required: [true, 'Birth date is required']
  },
  gender: {
    type: String,
    enum: ['male', 'female']
  },
  isVerified: {
    type: Boolean,
    default: false
  },
  requestId: {
    type: String,
    unique: true,
    sparse: true,  // Allows null values while maintaining uniqueness for non-null values
    default: null
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  idCardFace: {
    type: String,  // Store base64 image
    default: null
  }
});

// Hash password and generate request ID before saving
userSchema.pre('save', async function(next) {
  // Hash password if it's modified
  if (this.isModified('password')) {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
  }

  // Generate request ID for new users (only on creation, not updates)
  if (this.isNew && !this.requestId) {
    this.requestId = this.generateRequestId();
  }

  next();
});

// Method to check password
userSchema.methods.matchPassword = async function(enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Method to generate unique request ID
userSchema.methods.generateRequestId = function() {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 15);
  return `req_${timestamp}_${randomStr}`;
};

const User = mongoose.model('User', userSchema);

export default User;
