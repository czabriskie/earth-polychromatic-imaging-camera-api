# NASA EPIC API Client

A Python client for NASA's Earth Polychromatic Imaging Camera (EPIC) API.

## Project Structure

```
src/
├── earth_polychromatic_api/    # Main API client package
│   ├── __init__.py
│   └── client.py              # EpicApiClient class
└── tests/                     # Test suite
    ├── __init__.py
    ├── test_epic_api.py       # Comprehensive unit tests
    └── test_datasets/         # Mock API response data
        ├── natural_recent_response.json
        ├── enhanced_date_response.json
        ├── natural_all_dates_response.json
        ├── aerosol_recent_response.json
        ├── cloud_recent_response.json
        ├── enhanced_all_dates_response.json
        ├── aerosol_all_dates_response.json
        └── cloud_all_dates_response.json
```

## Installation

Install the test dependencies:
```bash
pip install -r requirements-test.txt
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test class:
```bash
pytest src/tests/test_epic_api.py::TestNaturalEndpoints -v
```

Run with coverage:
```bash
pytest --cov=earth_polychromatic_api
```

## API Endpoints Covered

The test suite covers all NASA EPIC API endpoints:

### Natural Color Imagery
- `GET /api/natural` - Most recent natural color images
- `GET /api/natural/date/{date}` - Natural images for specific date
- `GET /api/natural/all` - All available dates for natural images

### Enhanced Color Imagery
- `GET /api/enhanced` - Most recent enhanced color images
- `GET /api/enhanced/date/{date}` - Enhanced images for specific date
- `GET /api/enhanced/all` - All available dates for enhanced images

### Aerosol Index Imagery
- `GET /api/aerosol` - Most recent aerosol index images
- `GET /api/aerosol/date/{date}` - Aerosol images for specific date
- `GET /api/aerosol/all` - All available dates for aerosol images

### Cloud Fraction Imagery
- `GET /api/cloud` - Most recent cloud fraction images
- `GET /api/cloud/date/{date}` - Cloud images for specific date
- `GET /api/cloud/all` - All available dates for cloud images

### Image URL Builder
- `build_image_url()` - Constructs archive download URLs for images

## Test Features

- **Comprehensive Coverage**: Tests all API endpoints with proper arrange/act/assert structure
- **Mocked Responses**: Uses pytest monkeypatch with pre-built test data
- **Error Handling**: Tests HTTP error responses and edge cases
- **URL Construction**: Validates image archive URL building for all formats (PNG, JPG, thumbs)
- **Fixtures**: Organized test data fixtures for easy maintenance
- **Documentation**: Each test includes detailed docstrings explaining what it tests

## Test Data

All test responses are stored as JSON files in `src/tests/test_datasets/` and represent realistic API responses with proper metadata structure including:

- Image identifiers and timestamps
- Satellite position coordinates (DSCOVR J2000)
- Earth centroid coordinates
- Moon and sun positions
- Attitude quaternions
- Image captions and version info