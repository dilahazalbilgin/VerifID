import express from 'express';
import { 
  generateRequestId, 
  verifyUserByRequestId, 
  getMyRequestId, 
  revokeRequestId 
} from '../controllers/verificationController.js';
import { protect } from '../middleware/authMiddleware.js';

const router = express.Router();

// Protected routes (require authentication)
router.post('/generate-request-id', protect, generateRequestId);
router.get('/my-request-id', protect, getMyRequestId);
router.delete('/revoke-request-id', protect, revokeRequestId);

// Public route for third-party verification (no authentication required)
router.get('/verify/:requestId', verifyUserByRequestId);

export default router;
