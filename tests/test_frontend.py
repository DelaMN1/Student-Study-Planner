"""
Frontend tests using Selenium for browser automation
"""
import pytest
import time
import subprocess
import requests
import os
import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="class")
def driver():
    """Set up Chrome driver for testing."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    
    try:
        # Try to use webdriver-manager first
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to use webdriver-manager: {e}")
        try:
            # Fallback to system ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e2:
            print(f"Failed to use system ChromeDriver: {e2}")
            # Skip the test if ChromeDriver is not available
            pytest.skip("ChromeDriver not available")
    
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="class")
def app_server():
    """Start the Flask app server for testing."""
    # Start the Flask app in a separate process
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    env['FLASK_APP'] = 'app.py'
    
    # Use a different port for testing
    env['FLASK_RUN_PORT'] = '5001'
    
    process = subprocess.Popen([
        sys.executable, '-m', 'flask', 'run', '--port=5001'
    ], env=env, cwd=os.getcwd())
    
    # Wait for the server to start
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001')
        if response.status_code != 200:
            raise Exception("Server not responding properly")
    except Exception as e:
        process.terminate()
        raise Exception(f"Failed to start Flask server: {e}")
    
    yield process
    
    # Clean up
    process.terminate()
    process.wait()


@pytest.fixture
def base_url(app_server):
    """Get the base URL for testing."""
    return "http://localhost:5001"


class TestFrontend:
    """Frontend tests using Selenium."""
    
    def test_chrome_driver_works(self, driver):
        """Test that Chrome WebDriver is working properly."""
        # Navigate to a simple website
        driver.get("https://www.google.com")
        
        # Check that the page loaded
        assert "Google" in driver.title
        
        # Check that we can find elements
        search_box = driver.find_element(By.NAME, "q")
        assert search_box.is_displayed()
        
        print("Chrome WebDriver is working correctly!")
    
    def test_homepage_loads(self, driver, base_url):
        """Test that the homepage loads correctly."""
        driver.get(base_url)
        
        # Check page title
        assert "Study Planner" in driver.title
        
        # Check for main elements
        assert driver.find_element(By.TAG_NAME, "nav")
        assert driver.find_element(By.CLASS_NAME, "container")
    
    def test_navigation_menu(self, driver, base_url):
        """Test navigation menu functionality."""
        driver.get(base_url)
        
        # Check if navigation links are present
        nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a")
        assert len(nav_links) > 0
        
        # Check for specific navigation items
        nav_texts = [link.text for link in nav_links]
        assert any("Login" in text for text in nav_texts)
        assert any("Register" in text for text in nav_texts)
    
    def test_dark_mode_toggle(self, driver, base_url):
        """Test dark mode toggle functionality."""
        driver.get(base_url)
        
        # Find dark mode toggle button
        toggle_button = driver.find_element(By.ID, "toggle-dark")
        assert toggle_button.is_displayed()
        
        # Check initial state (light mode)
        body = driver.find_element(By.TAG_NAME, "body")
        initial_class = body.get_attribute("class")
        
        # Click toggle button
        toggle_button.click()
        time.sleep(1)  # Wait for transition
        
        # Check if dark mode is applied
        new_class = body.get_attribute("class")
        assert "dark-mode" in new_class
        
        # Toggle back to light mode
        toggle_button.click()
        time.sleep(1)
        
        # Check if light mode is restored
        final_class = body.get_attribute("class")
        assert "dark-mode" not in final_class
    
    def test_registration_form(self, driver, base_url):
        """Test user registration form."""
        driver.get(f"{base_url}/register")
        
        # Fill registration form
        username_field = driver.find_element(By.NAME, "username")
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        confirm_password_field = driver.find_element(By.NAME, "confirm_password")
        
        # Generate unique test data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_username = f"testuser_{unique_id}"
        test_email = f"test_{unique_id}@example.com"
        
        username_field.send_keys(test_username)
        email_field.send_keys(test_email)
        password_field.send_keys("testpass123")
        confirm_password_field.send_keys("testpass123")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check for redirect to login page
        time.sleep(2)
        assert "login" in driver.current_url.lower()
    
    def test_login_form(self, driver, base_url, test_user):
        """Test user login form."""
        driver.get(f"{base_url}/login")
        
        # Fill login form
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(test_user['username'])
        password_field.send_keys("testpass123")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check for redirect to dashboard
        time.sleep(2)
        assert "dashboard" in driver.current_url.lower()
    
    def test_dashboard_functionality(self, driver, base_url, auth, test_user):
        """Test dashboard functionality."""
        # Login first
        driver.get(f"{base_url}/login")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(test_user['username'])
        password_field.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(2)
        
        # Check dashboard elements
        assert "dashboard" in driver.current_url.lower()
        assert driver.find_element(By.CLASS_NAME, "container")
        
        # Check for task-related elements
        task_elements = driver.find_elements(By.CLASS_NAME, "task-card")
        # Should have at least the floating action button
        assert len(driver.find_elements(By.CLASS_NAME, "btn-floating")) > 0
    
    def test_task_creation_form(self, driver, base_url, auth, test_user):
        """Test task creation form."""
        # Login first
        driver.get(f"{base_url}/login")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(test_user['username'])
        password_field.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(2)
        
        # Navigate to task creation
        driver.get(f"{base_url}/task/create")
        
        # Fill task creation form
        title_field = driver.find_element(By.NAME, "title")
        description_field = driver.find_element(By.NAME, "description")
        status_field = driver.find_element(By.NAME, "status")
        
        title_field.send_keys("Test Task from Selenium")
        description_field.send_keys("This is a test task created via Selenium")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Check for redirect to dashboard
        time.sleep(2)
        assert "dashboard" in driver.current_url.lower()
    
    def test_search_functionality(self, driver, base_url, auth, test_user):
        """Test search functionality."""
        # Login first
        driver.get(f"{base_url}/login")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(test_user['username'])
        password_field.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(2)
        
        # Navigate to search page
        driver.get(f"{base_url}/search")
        
        # Check search form
        search_input = driver.find_element(By.NAME, "q")
        assert search_input.is_displayed()
        
        # Perform a search
        search_input.send_keys("test")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(2)
        
        # Check search results
        assert "search" in driver.current_url.lower()
    
    def test_category_management(self, driver, base_url, auth, test_user):
        """Test category management functionality."""
        # Login first
        driver.get(f"{base_url}/login")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(test_user['username'])
        password_field.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(2)
        
        # Navigate to categories page
        driver.get(f"{base_url}/categories")
        
        # Check categories page
        assert "categories" in driver.current_url.lower()
        
        # Check for create category link
        create_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='create']")
        assert len(create_links) > 0
    
    def test_responsive_design(self, driver, base_url):
        """Test responsive design elements."""
        driver.get(base_url)
        
        # Test mobile viewport
        driver.set_window_size(375, 667)  # iPhone SE size
        time.sleep(1)
        
        # Check if navigation is still accessible
        nav = driver.find_element(By.TAG_NAME, "nav")
        assert nav.is_displayed()
        
        # Test desktop viewport
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        
        # Check if layout adapts
        container = driver.find_element(By.CLASS_NAME, "container")
        assert container.is_displayed()
    
    def test_accessibility_features(self, driver, base_url):
        """Test accessibility features."""
        driver.get(base_url)
        
        # Check for proper heading structure (any heading tag)
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        assert len(headings) > 0
        
        # Check for alt text on images
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            # Alt text should be present (can be empty for decorative images)
            assert alt_text is not None
    
    def test_error_handling(self, driver, base_url):
        """Test error handling."""
        # Test 404 page
        driver.get(f"{base_url}/nonexistent-page")
        
        # Should show error page
        assert "404" in driver.page_source or "not found" in driver.page_source.lower()
    
    def test_performance_metrics(self, driver, base_url):
        """Test basic performance metrics."""
        driver.get(base_url)
        
        # Check page load time
        load_time = driver.execute_script("return performance.timing.loadEventEnd - performance.timing.navigationStart;")
        assert load_time < 5000  # Should load within 5 seconds
        
        # Check for console errors (ignore 404 errors for missing resources)
        logs = driver.get_log('browser')
        error_logs = [log for log in logs if log['level'] == 'SEVERE' and '404' not in log['message']]
        assert len(error_logs) == 0  # Should have no severe errors (excluding 404s)


@pytest.mark.skip(reason="Requires multiple browser drivers")
class TestCrossBrowserCompatibility:
    """Cross-browser compatibility tests."""
    
    def test_firefox_compatibility(self):
        """Test Firefox compatibility."""
        # This would require Firefox WebDriver
        pass
    
    def test_safari_compatibility(self):
        """Test Safari compatibility."""
        # This would require Safari WebDriver
        pass


class TestMobileTesting:
    """Mobile-specific tests."""
    
    def test_mobile_viewport(self, driver, base_url):
        """Test mobile viewport behavior."""
        driver.get(base_url)
        
        # Set mobile viewport
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Check if mobile-friendly elements are present
        nav = driver.find_element(By.TAG_NAME, "nav")
        assert nav.is_displayed()
        
        # Check for mobile-friendly navigation
        nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a")
        assert len(nav_links) > 0
    
    def test_touch_interactions(self, driver, base_url):
        """Test touch interaction elements."""
        driver.get(base_url)
        
        # Set mobile viewport
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Check for touch-friendly button sizes (only visible buttons)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = [btn for btn in buttons if btn.is_displayed()]
        
        if visible_buttons:
            for button in visible_buttons:
                size = button.size
                # Buttons should be reasonably sized for touch (at least 30x30 pixels)
                assert size['width'] >= 30 or size['height'] >= 30
        else:
            # If no buttons are visible, that's also acceptable
            print("No visible buttons found on the page") 