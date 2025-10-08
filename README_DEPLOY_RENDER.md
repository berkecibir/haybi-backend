# haybi-backend Deployment Guide

## Deploy to Render

1) Push to GitHub (repo: haybi-backend)

2) Login to Render.com, New -> Web Service
   - Connect to GitHub, select repo
   - Root: repository, Branch: main
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3) Environment Variables:
   - API_KEY (optional but recommended for security)
   - FALAI_API_KEY (required for image processing)
   - DATABASE_URL
   - ALLOWED_ORIGINS

4) Deploy and get URL. Frontend will make requests to this URL.

## CORS Configuration

For development, you can set `ALLOWED_ORIGINS=*` to allow requests from any origin.
For production, specify exact origins like:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Authentication

The backend now supports flexible authentication:
- `/api/jobs` endpoint does NOT require authentication (for easier frontend integration)
- `/edit-image/` endpoint DOES require authentication (for security)

If API_KEY is not configured on the server, authentication is skipped automatically.

## Health Check

The backend includes a health check endpoint at `/health` that you can use to verify the service is running:
```
GET https://haybi-backend.onrender.com/health
```

This should return:
```json
{"status": "healthy"}
```

## Docker Deployment (Optional)

You can also deploy using Docker:

```bash
docker build -t haybi-backend .
docker run -p 8000:8000 haybi-backend
```

## Flutter Integration Example

### Create Job (image + prompt): `POST /api/jobs` multipart/form-data
- Field `image`: file
- Field `prompt`: text
- Returns: `{ "job_id": "..." }`

Dart (http, multipart) example:

```dart
import 'package:http/http.dart' as http;
import 'dart:io';
import 'dart:convert';

Future<String?> createJob(File imageFile, String prompt) async {
  var uri = Uri.parse('https://haybi-backend.onrender.com/api/jobs');
  var req = http.MultipartRequest('POST', uri);
  req.fields['prompt'] = prompt;
  req.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
  var res = await req.send();
  if (res.statusCode == 200) {
    final body = await res.stream.bytesToString();
    return jsonDecode(body)['job_id'];
  } else {
    throw Exception('Job creation failed: ${res.statusCode}');
  }
}
```

### Check Job Status: `GET /api/jobs/{job_id}` (polling recommended)
```dart
Future<Map<String, dynamic>> getJob(String jobId) async {
  final uri = Uri.parse('https://haybi-backend.onrender.com/api/jobs/$jobId');
  final res = await http.get(uri);
  if (res.statusCode == 200) return jsonDecode(res.body);
  throw Exception('Job fetch failed');
}
```

### Create Job with Authentication (if API_KEY is configured): `POST /edit-image/` multipart/form-data
```dart
Future<String?> createJobWithAuth(File imageFile, String prompt, String apiKey) async {
  var uri = Uri.parse('https://haybi-backend.onrender.com/edit-image/');
  var req = http.MultipartRequest('POST', uri);
  req.headers['Authorization'] = 'Bearer $apiKey';
  req.fields['prompt'] = prompt;
  req.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
  var res = await req.send();
  if (res.statusCode == 200) {
    final body = await res.stream.bytesToString();
    return jsonDecode(body)['job_id'];
  } else {
    throw Exception('Job creation failed: ${res.statusCode}');
  }
}
```

## Troubleshooting

### "sunucuya bağlanılamadı" (Server connection failed) Error

If you're getting this error, check:

1. **Deployment Status**: Verify in Render dashboard that your service is deployed successfully
2. **Environment Variables**: Ensure all required variables are set (FALAI_API_KEY, DATABASE_URL, ALLOWED_ORIGINS)
3. **Start Command**: Make sure it's set to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Health Check**: Visit `https://haybi-backend.onrender.com/health` to verify the service is running
5. **CORS Configuration**: Ensure ALLOWED_ORIGINS includes your frontend origin

### Common Issues and Solutions

1. **Service not starting**: Check Render logs for error messages
2. **CORS errors**: Verify ALLOWED_ORIGINS environment variable
3. **Timeout errors**: The service might be slow to start on Render's free tier
4. **Authentication errors**: Check if API_KEY is properly configured

## Notes

- Add parsing and image saving in `falai_client.py` according to fal.ai response format (example: base64 -> save file).
- Apply CORS restrictions with ALLOWED_ORIGINS environment variable.
- In production, move uploads folder to persistent storage like S3/MinIO.