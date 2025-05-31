import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import connectDB from './config/db.js';
import userRoutes from './routes/userRoutes.js';

// Load environment variables
dotenv.config();

// Connect to database
connectDB();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json()); // This line is crucial for parsing JSON bodies
app.use(express.urlencoded({ extended: true })); // Add this for form data

// Add this before your routes
app.use((req, res, next) => {
  console.log('Request Body:', req.body);
  console.log('Content Type:', req.headers['content-type']);
  next();
});

// Routes
app.use('/api/users', userRoutes);

app.get('/', (req, res) => {
  res.send('VerifID API is running');
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});


