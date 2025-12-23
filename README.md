# AuctionNet 🎯

Real-time online auction platform built with Vue.js and Flask.

## Main Features

- **JWT Authentication** - Secure user login and registration
- **Real-time Auctions** - Live bidding with WebSocket updates
- **Image Upload** - Support for both URL and local file uploads
- **User Profile Management** - Track participations, created auctions, and wins
- **Advanced Filters** - Search by category, status, and price
- **Real-time Notifications** - Instant updates for bid placements and auction status

## Frameworks Used

### Frontend
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vue Router 4** - Official router for Vue.js
- **Vite** - Next-generation frontend build tool

### Backend
- **Flask 3.0** - Lightweight Python web framework
- **Flask-SocketIO** - WebSocket integration for real-time features
- **Flask-JWT-Extended** - JWT authentication
- **Pydantic** - Data validation using Python type annotations

### Additional Technologies
- **Docker** - Containerization for deployment
- **Gunicorn** - Production WSGI server
- **Nginx** - Reverse proxy and static file server
- **YAML** - Lightweight database storage

## Linters Used

- **ESLint** - JavaScript/Vue.js code linting
- **Prettier** (optional) - Code formatting
- **Pylint** (optional) - Python code analysis

## Installation Guide

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **Docker** (optional, for deployment)

## Installation

### Option 1: Using Docker

```bash
# Build the images
docker compose build

# Start the containers
docker compose up -d
```

Accessible at: http://localhost:5173/

### Option 2: Without Docker

#### Backend Setup (Flask)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
# Or on Mac:
python3 app.py
```

The backend will be available at `http://localhost:5000`

#### Frontend Setup (Vue.js)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Docker Setup (Production)

#### Using Docker Compose

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

#### Individual Images

**Backend:**
```bash
cd backend
docker build -t auctionnet-backend .
docker run -p 5000:5000 auctionnet-backend
```

**Frontend:**
```bash
cd frontend
docker build -t auctionnet-frontend .
docker run -p 80:80 auctionnet-frontend
```

## Basic Usage Guide

### 1. Register/Login
- Navigate to `/login` to create an account or sign in
- JWT token is stored locally for authentication

### 2. Browse Auctions
- View all active auctions on the home page
- Use filters to find specific categories or price ranges
- Search by keywords in auction titles

### 3. Create an Auction
- Click on the "Sell" button
- Fill in product details (title, description, category)
- Upload an image (URL or local file)
- Set starting price and auction duration
- Submit to create your auction

### 4. Place Bids
- Click on an auction to view details
- Enter your bid amount (must exceed current price + minimum increment)
- Confirm your bid
- Real-time updates will show new bids from other users

### 5. Manage Profile
- Access your profile to view:
  - Participated auctions
  - Created auctions
  - Won auctions
- Credit your account balance for bidding

### 6. Real-time Updates
- WebSocket connection provides instant notifications
- Auction status updates automatically
- See new bids as they happen

## Project Structure

```
AuctionNet-Prod/
├── backend/              # Flask API + WebSocket
│   ├── app.py           # Main entry point
│   ├── models/          # Pydantic schemas
│   ├── services/        # Business logic
│   │   ├── auth.py      # Authentication service
│   │   ├── auctions.py  # Auction management
│   │   └── repo.py      # YAML repository
│   └── local_data/      # YAML database
│       ├── db/          # Data files
│       └── media/       # Uploaded images
├── frontend/            # Vue.js application
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── views/       # Page components
│   │   ├── services/    # API & WebSocket clients
│   │   ├── router/      # Route configuration
│   │   └── assets/      # Static assets
│   └── public/          # Public assets
└── docker-compose.yml   # Docker orchestration
```

## Environment Variables

### Backend (.env)
```env
JWT_SECRET_KEY=your-secret-key-here
DB_DIR=./local_data/db
MEDIA_DIR=./local_data/media
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:5000
```

## API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/register
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /api/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Auction Endpoints

#### Get All Auctions
```http
GET /api/auctions?status=running&category=electronics
```

#### Get Auction Details
```http
GET /api/auctions/{auction_id}
```

#### Create Auction
```http
POST /api/auctions
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "product_id": "p_123",
  "start_price": 100.00,
  "min_increment": 5.00,
  "start_at": "2025-12-25T10:00:00Z",
  "end_at": "2025-12-30T10:00:00Z"
}
```

#### Place Bid
```http
POST /api/auctions/{auction_id}/bids
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "amount": 105.00
}
```

### Product Endpoints

#### Create Product
```http
POST /api/products
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "title": "iPhone 15 Pro",
  "description": "Brand new, sealed",
  "category": "electronics",
  "condition": "new",
  "images": ["https://example.com/image.jpg"]
}
```

### User Endpoints

#### Get User Profile
```http
GET /api/me
Authorization: Bearer {jwt_token}
```

#### Credit Account
```http
POST /api/me/credit
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "amount": 500.00
}
```

### WebSocket Events

Connect to WebSocket at `ws://localhost:5000`

**Client Events:**
- `join` - Join auction room
- `leave` - Leave auction room

**Server Events:**
- `bid_placed` - New bid notification
- `auction_created` - New auction notification
- `auction_ended` - Auction completion notification

## Useful Commands

### Frontend
```bash
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend
```bash
pytest               # Run unit tests
python -m pip freeze > requirements.txt  # Update dependencies
```

## Deployment

### Railway Deployment

The project is configured for Railway with:
- **Nginx** for frontend (SPA routing support)
- **Gunicorn** for backend (production WSGI server)
- **WebSocket** support enabled
- Optimized Docker images using Alpine Linux

### Environment Configuration
Ensure you set the following environment variables in Railway:
- `JWT_SECRET_KEY` - Strong random secret for JWT
- `VITE_API_BASE_URL` - Backend API URL

## License

MIT License - Feel free to use this project for educational purposes.

## Contributors

- **Milton** - Full Stack Development

---

**Polytech Paris Saclay - Web & Mobile Dev 2 - 2025/2026**

## Online Deployment

We use Railway for deployment which allows hosting our website for 1 month for free.

**Railway Configuration:**
- Connected to our main branch
- Created two services (1 per container)
- Railway automatically detects and runs the Dockerfile
