import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import path from 'path';
import { db } from './db';
import routes from './routes/index';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

async function initializeDatabase() {
  try {
    await db.connect();
    console.log('✅ Database connected successfully');
  } catch (error) {
    console.error('❌ Failed to connect to database:', error);
    process.exit(1);
  }
}

initializeDatabase();

const allowedOrigins = [
  process.env.CLIENT_URL,
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  'http://localhost:3001',
  'http://127.0.0.1:3001',
  'https://localhost:3000',
  'https://127.0.0.1:3000'
].filter(Boolean);

const corsOptions = {
  origin: true, 
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'],
  allowedHeaders: [
    'Content-Type', 
    'Authorization', 
    'X-Requested-With', 
    'Accept',
    'Origin',
    'Access-Control-Request-Method',
    'Access-Control-Request-Headers',
    'X-API-Key'
  ],
  exposedHeaders: [
    'Content-Range',
    'X-Content-Range'
  ],
  maxAge: 86400,
  optionsSuccessStatus: 204
};

app.use(cors(corsOptions));

// app.use(helmet({
//   crossOriginResourcePolicy: { policy: "cross-origin" }
// }));


app.use(morgan('combined'));

app.use(express.json({
  limit: '10mb'
}));

app.use(express.urlencoded({ 
  extended: true,
  limit: '10mb'
}));

app.options('*', cors(corsOptions));

app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    service: 'GradeUp API',
    version: '1.0.0',
    cors: {
      origin: req.headers.origin || 'No origin header',
      allowed: true
    }
  });
});

app.get('/test', (req, res) => {
  res.json({ 
    success: true,
    message: 'Server is working correctly! ✅',
    timestamp: new Date().toISOString(),
    cors: {
      origin: req.headers.origin || 'No origin header',
      method: req.method
    }
  });
});

app.use('/api', routes);

app.use(express.static(path.join(__dirname, '..', 'public')));

app.get('*', (req, res) => {
  if (!req.path.startsWith('/api') && !req.path.startsWith('/health') && !req.path.startsWith('/test')) {
    res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
  }
});

app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err.message);
  
  if (err.message === 'Not allowed by CORS') {
    return res.status(403).json({ 
      success: false,
      error: 'CORS policy: Origin not allowed',
      origin: req.headers.origin,
      allowed_origins: allowedOrigins,
      timestamp: new Date().toISOString()
    });
  }
  
  res.status(500).json({ 
    success: false,
    error: 'Internal server error',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log(`🚀 GradeUp API Server started successfully!`);
  console.log('='.repeat(60));
  console.log(`📍 Port: ${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`⏰ Started at: ${new Date().toISOString()}`);
  console.log('');
  console.log('🔧 CORS Configuration:');
  console.log('   ✅ CORS enabled');
  console.log('   🌐 Allowed origins:');
  allowedOrigins.forEach(origin => console.log(`      • ${origin}`));
  console.log('');
  console.log('🔗 Available Endpoints:');
  console.log('   📋 Root API info  → http://localhost:3001/');
  console.log('   ❤️  Health check   → http://localhost:3001/health');
  console.log('   🧪 Test endpoint   → http://localhost:3001/test');
  console.log('   👥 Users API       → http://localhost:3001/api/users');
  console.log('');
  console.log('📝 Logs:');
  console.log('   • Morgan combined format enabled');
  console.log('   • CORS enabled with credentials');
  console.log('='.repeat(60));
});

export default app;