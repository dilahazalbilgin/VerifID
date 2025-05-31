import express from 'express';
import { registerUser, loginUser, updateUserProfile } from '../controllers/userController.js';
import { protect } from '../middleware/authMiddleware.js';

const router = express.Router();

router.post('/', registerUser);
router.post('/login', loginUser);
router.put('/profile', protect, updateUserProfile);

export default router;
