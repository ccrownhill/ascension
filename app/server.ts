import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { spawn } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 8080;

// Enable CORS for requests from the frontend
app.use(cors({
  origin: (origin, callback) => {
    // Allow any localhost origin during development
    if (!origin || /^http:\/\/localhost(:\d+)?$/.test(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST'],
  credentials: true
}));

// Create downloads directory if it doesn't exist
const downloadsDir = path.join(__dirname, 'downloads');
if (!fs.existsSync(downloadsDir)) {
  fs.mkdirSync(downloadsDir, { recursive: true });
}

// Configure multer for file uploads
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      cb(null, downloadsDir);
    },
    filename: (req, file, cb) => {
      // Use original filename
      cb(null, file.originalname);
    }
  }),
  fileFilter: (req, file, cb) => {
    // Accept only PDF and DOCX files
    const allowedMimes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

// Endpoint to handle CV uploads
app.post('/api/upload-cv', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = path.join(downloadsDir, req.file.filename);
  const projectRoot = path.join(__dirname, '..');

  // Spawn the Python script without waiting for it to complete
  const pythonProcess = spawn('python3', [path.join(projectRoot, 'auto_apply.py'), filePath], {
    cwd: projectRoot, // Set working directory to project root
    detached: true, // Allow the process to run independently
    stdio: 'pipe' // Capture output
  });

  // Log output for debugging
  pythonProcess.stdout?.on('data', (data) => {
    console.log(`[auto_apply.py] ${data}`);
  });

  pythonProcess.stderr?.on('data', (data) => {
    console.error(`[auto_apply.py ERROR] ${data}`);
  });

  pythonProcess.on('error', (err) => {
    console.error(`[auto_apply.py] Failed to spawn: ${err}`);
  });

  // Unref the process so Node doesn't wait for it
  pythonProcess.unref();

  // Return success immediately without waiting for the script
  res.json({
    success: true,
    message: 'File uploaded and script triggered',
    filePath: filePath
  });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

server.on('error', (err: any) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Error: Port ${PORT} is already in use.`);
    console.error('Please free up port 8081 or kill the process using it.');
    console.error(`To find the process: lsof -i :${PORT}`);
    console.error(`To kill it: kill <PID>`);
    process.exit(1);
  } else {
    throw err;
  }
});
