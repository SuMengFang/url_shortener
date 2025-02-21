# URL Shortener API Documentation

## Overview

This API provides functionality to shorten URLs and redirect users when they access the short URL. The system enforces rate limiting and expiration policies.

## Base URL

```
http://<server-ip>:5000
```

## API Endpoints

### 1. Create Short URL

**Endpoint:**

```
POST /urls
```

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "original_url": "https://example.com"
}
```

**Response:**

- **Success (201):**

```json
{
  "short_url": "http://<server-ip>:5000/r/abc12345",
  "expiration_date": "YYYY-MM-DD HH:MM:SS",
  "success": true
}
```

- **Existing URL (200):**

```json
{
  "short_url": "http://<server-ip>:5000/r/abc12345",
  "expiration_date": "YYYY-MM-DD HH:MM:SS",
  "success": true
}
```

- **Error Responses:**
  - 400 Bad Request: Missing or invalid parameters
  - 409 Conflict: Short URL already exists
  - 429 Too Many Requests: Rate limit exceeded

#### **Rate Limiting:**
- Max **3 requests per minute per IP**

### 2. Redirect to Original URL

**Endpoint:**

```
GET /r/<short_code>
```

#### **Behavior:**
- Redirects to the original URL (302 Found)

#### **Error Responses:**
- **400 Bad Request:** Invalid short URL format
- **404 Not Found:** Short URL does not exist
- **410 Gone:** Short URL expired

---

## Running the API with Docker

### Build and Run the Docker Container

1. **Build the Docker image:**

```
docker build -t url-shortener .
```

2. **Run the container:**

```
docker run -d -p 5000:5000 --name url-shortener url-shortener
```

### Pull and Run from Docker Hub

1. **Pull the Docker image:**

```
docker pull et23518779/shorturl:latest
```

2. **Run the container:**

```
docker run -d -p 5000:5000 --name url-shortener et23518779/shorturl
```

---

## Rate Limiting

- The API is rate-limited to **5 requests per minute per IP** globally.
- The `/urls` endpoint has an additional limit of **3 requests per minute** per IP.

---

## Technologies Used
- **Flask**: Web framework
- **SQLite**: Database storage
- **Flask-Limiter**: Rate limiting
- **Docker**: Containerization
- **SQLAlchemy**: ORM for database operations

---

## Notes
- The short URL expires **30 days** after creation.
- If a URL is already shortened, the same short URL is returned instead of generating a new one.
- Rate limiting is enforced to prevent abuse.

