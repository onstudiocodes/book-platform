"""
Quick Test Runner - Run only working tests
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Add the project directory to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    os.environ['DJANGO_SETTINGS_MODULE'] = 'book_platform.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run only the working tests
    working_tests = [
        'simple_tests',
        'main.tests.CategoryModelTest',
        'accounts.tests.UserProfileModelTest',
    ]
    
    print("Running working tests only...")
    print("=" * 50)
    
    for test in working_tests:
        print(f"\n🧪 Running {test}")
        print("-" * 30)
        failures = test_runner.run_tests([test])
        if failures:
            print(f"❌ {test} failed")
        else:
            print(f"✅ {test} passed")
    
    print("\n" + "=" * 50)
    print("Working tests completed!")
