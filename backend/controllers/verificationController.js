import User from '../models/User.js';

// @desc    Generate request ID for user (for third-party verification)
// @route   POST /api/verification/generate-request-id
// @access  Private
export const generateRequestId = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Check if user is verified
    if (!user.isVerified) {
      return res.status(400).json({ 
        message: 'User must be verified before generating request ID' 
      });
    }

    // Generate new request ID if user doesn't have one or wants to regenerate
    const newRequestId = user.generateRequestId();
    user.requestId = newRequestId;
    await user.save();

    res.json({
      success: true,
      message: 'Request ID generated successfully',
      requestId: newRequestId,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        isVerified: user.isVerified
      }
    });
  } catch (error) {
    console.error('Generate request ID error:', error);
    res.status(500).json({ 
      message: 'Server error occurred while generating request ID',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};

// @desc    Verify user status by request ID (for third-party apps)
// @route   GET /api/verification/verify/:requestId
// @access  Public (for third-party apps)
export const verifyUserByRequestId = async (req, res) => {
  try {
    const { requestId } = req.params;

    if (!requestId) {
      return res.status(400).json({ 
        success: false,
        message: 'Request ID is required' 
      });
    }

    // Find user by request ID
    const user = await User.findOne({ requestId }).select('-password -__v');

    if (!user) {
      return res.status(404).json({ 
        success: false,
        message: 'Invalid request ID or user not found',
        verified: false
      });
    }

    // Return verification status and basic user info
    res.json({
      success: true,
      message: 'User verification status retrieved successfully',
      verified: user.isVerified,
      requestId: user.requestId,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        idCardNumber: user.idCardNumber,
        isVerified: user.isVerified,
        verifiedAt: user.isVerified ? user.updatedAt : null
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Verify user by request ID error:', error);
    res.status(500).json({ 
      success: false,
      message: 'Server error occurred during verification',
      verified: false,
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};

// @desc    Get current user's request ID
// @route   GET /api/verification/my-request-id
// @access  Private
export const getMyRequestId = async (req, res) => {
  try {
    const user = await User.findById(req.user._id).select('requestId isVerified firstName lastName email');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({
      success: true,
      requestId: user.requestId,
      isVerified: user.isVerified,
      hasRequestId: !!user.requestId,
      user: {
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Get request ID error:', error);
    res.status(500).json({ 
      message: 'Server error occurred while retrieving request ID',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};

// @desc    Revoke/delete request ID (security feature)
// @route   DELETE /api/verification/revoke-request-id
// @access  Private
export const revokeRequestId = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (!user.requestId) {
      return res.status(400).json({ 
        message: 'No request ID found to revoke' 
      });
    }

    const oldRequestId = user.requestId;
    user.requestId = null;
    await user.save();

    res.json({
      success: true,
      message: 'Request ID revoked successfully',
      revokedRequestId: oldRequestId
    });
  } catch (error) {
    console.error('Revoke request ID error:', error);
    res.status(500).json({ 
      message: 'Server error occurred while revoking request ID',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
};
