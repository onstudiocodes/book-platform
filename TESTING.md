# Testing Guide for Book Platform

This document provides comprehensive information about testing the Book Platform Django application.

## Overview

The Book Platform project includes extensive test coverage across all major components:

- **Model Tests**: Database models, relationships, and methods
- **View Tests**: HTTP responses, templates, and user interactions
- **Form Tests**: Form validation, widgets, and data processing
- **API Tests**: REST endpoints, serializers, and permissions
- **Integration Tests**: Cross-app functionality and workflows
- **Security Tests**: Authentication, authorization, and input validation

## Test Structure

```
book-platform/
├── main/tests.py           # Main app tests (books, categories, comments)
├── accounts/tests.py       # User management and authentication tests
├── author/tests.py         # Author dashboard and content management tests
├── news/tests.py          # News articles and API tests
├── travel/tests.py        # Travel stories and image upload tests
├── test_runner.py         # Simple test runner script
├── run_all_tests.py       # Comprehensive test suite runner
└── test_requirements.txt  # Testing dependencies
```

## Quick Start

### Running All Tests

```bash
# Basic test run
python manage.py test

# With our custom runner
python test_runner.py

# Fast mode with optimized settings
python test_runner.py --fast

# With coverage report
python test_runner.py --coverage
```

### Running Specific App Tests

```bash
# Test individual apps
python manage.py test main
python manage.py test accounts
python manage.py test author
python manage.py test news
python manage.py test travel

# Using custom runner
python test_runner.py main
python test_runner.py accounts --coverage
```

### Running Specific Test Classes

```bash
# Test specific functionality
python manage.py test main.tests.BookModelTest
python manage.py test accounts.tests.AuthenticationViewsTest
python manage.py test author.tests.AuthorFormsTest
```

## Test Categories

### 1. Model Tests

Test database models, relationships, and custom methods:

**Main App Models:**
- `CategoryModelTest`: Category creation and slug generation
- `BookModelTest`: Book CRUD, likes/dislikes, reading time
- `NewsModelTest`: News articles, categories, image handling
- `TravelStoryModelTest`: Travel stories, locations, metadata
- `CommentModelTest`: Comment system, replies, relationships

**Accounts App Models:**
- `UserProfileModelTest`: User profiles, statistics, methods
- `UserFollowModelTest`: Follow relationships, constraints

**Key Features Tested:**
- Model creation and validation
- Custom manager methods (e.g., `PublicBookManager`)
- String representations (`__str__` methods)
- URL generation (`get_absolute_url`)
- Custom model methods (likes_count, reading_time)
- Database constraints and relationships

### 2. View Tests

Test HTTP responses, templates, and user interactions:

**Public Views:**
- Index page with book listings
- Book detail views with view tracking
- Search functionality
- Profile pages
- News and travel story displays

**Authenticated Views:**
- Dashboard and analytics
- Content creation and editing
- User profile management
- Collection management

**AJAX/JSON Views:**
- Like/unlike functionality
- Comment submission
- Infinite scroll pagination
- Reading time tracking

**Key Features Tested:**
- HTTP status codes (200, 302, 404, 403)
- Template rendering and context
- Authentication requirements
- Permission-based access control
- Form processing and validation
- JSON response formats

### 3. Form Tests

Test form validation, widgets, and data processing:

**Main Forms:**
- `BookUploadForm`: Book creation with file uploads
- `TravelStoryForm`: Travel story with location data
- `NewsForm`: News article creation
- `ProfileForm`: User profile updates

**File Upload Handling:**
- Image uploads for thumbnails
- Multiple image uploads for galleries
- Audio file uploads
- File validation and processing

**Key Features Tested:**
- Form field validation
- File upload handling
- Widget attributes and styling
- Custom form methods
- Formset validation (NewsImageFormSet)

### 4. API Tests

Test REST API endpoints, serializers, and permissions:

**News API:**
- `NewsListCreateView`: List and create news articles
- Pagination and filtering
- Category-based filtering
- Authentication requirements

**Travel API:**
- `TravelStoryListAPIView`: Travel story listings
- Geographic data serialization
- Image relationship handling

**Comment API:**
- Comment creation and listing
- Permission-based access
- Nested comment support

**Key Features Tested:**
- HTTP status codes for API responses
- JSON response structure
- Serializer field validation
- Pagination functionality
- Authentication and permissions
- Query parameter filtering

### 5. Integration Tests

Test cross-app functionality and complex workflows:

**User Workflows:**
- Registration → Profile creation → Content creation
- Book reading → Time tracking → Analytics
- Following users → Content discovery
- Comment system across different content types

**Data Relationships:**
- Author-book relationships
- Category filtering across apps
- Comment system integration
- View tracking across content types

### 6. Security Tests

Test authentication, authorization, and input validation:

**Authentication Tests:**
- Login with username/email
- Password validation
- Session management
- Logout functionality

**Authorization Tests:**
- Content ownership verification
- Permission-based view access
- API endpoint protection

**Input Validation:**
- SQL injection prevention
- XSS protection
- File upload security
- Form input sanitization

## Test Database Configuration

Tests use optimized database settings for speed:

```python
# SQLite in-memory database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Simplified password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disabled migrations for speed
MIGRATION_MODULES = DisableMigrations()
```

## Test Data Creation

Tests create minimal, realistic data:

```python
# User creation
self.user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)

# Image creation for uploads
image_data = io.BytesIO()
img = Image.new('RGB', (100, 100), color='red')
img.save(image_data, format='JPEG')
test_image = SimpleUploadedFile(
    "test.jpg",
    image_data.getvalue(),
    content_type="image/jpeg"
)
```

## Coverage Requirements

Aim for high test coverage across:

- **Models**: 95%+ (all methods and relationships)
- **Views**: 85%+ (all user paths and edge cases)
- **Forms**: 90%+ (validation and file handling)
- **Utils**: 95%+ (utility functions and helpers)

Run coverage analysis:

```bash
# Generate coverage report
coverage run --source='.' manage.py test
coverage html
coverage report

# View in browser
open htmlcov/index.html
```

## Common Test Patterns

### Testing Views with Authentication

```python
def test_authenticated_view(self):
    self.client.login(username='testuser', password='testpass123')
    response = self.client.get(reverse('view_name'))
    self.assertEqual(response.status_code, 200)

def test_unauthenticated_redirect(self):
    response = self.client.get(reverse('protected_view'))
    self.assertEqual(response.status_code, 302)
    self.assertIn('/accounts/login', response.url)
```

### Testing File Uploads

```python
def test_image_upload(self):
    image_data = io.BytesIO()
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(image_data, format='JPEG')
    
    test_image = SimpleUploadedFile(
        "test.jpg",
        image_data.getvalue(),
        content_type="image/jpeg"
    )
    
    response = self.client.post(reverse('upload_view'), {
        'title': 'Test Upload',
        'image': test_image
    })
    self.assertEqual(response.status_code, 302)
```

### Testing API Endpoints

```python
def test_api_list(self):
    response = self.client.get(reverse('api:news-list'))
    self.assertEqual(response.status_code, 200)
    
    data = response.json()
    self.assertIn('results', data)
    self.assertEqual(len(data['results']), 1)

def test_api_create_authenticated(self):
    self.client.force_authenticate(user=self.user)
    response = self.client.post(reverse('api:news-list'), {
        'title': 'API News',
        'content': 'API content'
    })
    self.assertEqual(response.status_code, 201)
```

## Debugging Failed Tests

### Common Issues and Solutions

1. **Test Database Issues**
   ```bash
   # Clear test database
   python manage.py flush --settings=book_platform.test_settings
   ```

2. **File Upload Errors**
   - Ensure PIL/Pillow is installed
   - Check file permissions in test media directory
   - Verify content types match file formats

3. **Authentication Failures**
   - Check user creation in setUp methods
   - Verify login credentials
   - Ensure UserProfile exists for users

4. **API Test Failures**
   - Check authentication setup
   - Verify serializer fields
   - Confirm URL patterns are correct

### Verbose Test Output

```bash
# Maximum verbosity
python manage.py test --verbosity=3

# Debug specific test
python manage.py test main.tests.BookModelTest.test_book_creation --verbosity=3
```

## Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python manage.py test --settings=book_platform.test_settings
    coverage run --source='.' manage.py test
    coverage xml
```

## Performance Considerations

- Use `setUpClass` for expensive setup operations
- Minimize database queries in tests
- Use `TransactionTestCase` only when necessary
- Consider parallel test execution for large test suites

```bash
# Parallel test execution
python manage.py test --parallel auto
```

## Writing New Tests

When adding new features, ensure tests cover:

1. **Happy Path**: Normal, expected usage
2. **Edge Cases**: Boundary conditions and unusual inputs
3. **Error Handling**: Invalid data and error responses
4. **Permissions**: Authentication and authorization
5. **Integration**: How the feature works with existing code

### Test Naming Convention

```python
def test_feature_condition_expected_result(self):
    """Test that feature behaves correctly under specific condition"""
    pass

# Examples:
def test_book_creation_valid_data_success(self):
def test_login_invalid_credentials_error_message(self):
def test_api_unauthenticated_request_returns_401(self):
```

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Maintenance

Review and update tests regularly:

- After model changes, update related model tests
- When adding new views, add corresponding view tests
- Update API tests when serializers change
- Add regression tests for bug fixes
- Keep test data realistic but minimal
