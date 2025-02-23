from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import json
from datetime import datetime

class RealEstateScraper:
    def __init__(self):
        # Initialize Chrome options with additional settings to avoid detection
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')  # Commented out for debugging
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Add more realistic user agent
        self.options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        
        # Add additional preferences to make automation less detectable
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)

    def setup_driver(self):
        """Initialize the webdriver with enhanced settings"""
        self.driver = webdriver.Chrome(options=self.options)
        
        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)  # Increased wait time

    def scrape_zillow_listings(self, zip_code, timeout=60):
        """
        Scrape property listings for a given zip code with enhanced error handling and timeout
        Args:
            zip_code: The zip code to search
            timeout: Maximum time in seconds to spend on scraping
        """
        start_time = time.time()
        properties = []
        try:
            # Use a more specific search URL
            url = f"https://www.zillow.com/homes/for_sale/{zip_code}"
            print(f"Loading URL: {url}")
            self.driver.get(url)
            print("Page loaded, waiting for content...")
            
            # Add random delay to simulate human behavior
            time.sleep(5 + (time.time() % 3))
            
            print(f"Searching for properties in {zip_code}...")
            
            # Wait for search results to load
            # Check if we've exceeded our timeout
            if time.time() - start_time > timeout:
                print(f"Scraping timed out after {timeout} seconds")
                return properties

            try:
                print("Looking for property cards...")
                # First try to find the modern card class
                property_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.StyledPropertyCard-c11n-8-85-1__sc-14p766w-0"))
                )
            except TimeoutException:
                # If that fails, try the alternative card class
                try:
                    property_cards = self.wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test='property-card']"))
                    )
                except TimeoutException:
                    print("Could not find property listings. The page structure might have changed.")
                    return properties

            print(f"Found {len(property_cards)} properties")
            
            # Extract data from each property card
            for card in property_cards[:10]:  # Limit to 10 properties for demo
                try:
                    # Print the HTML of the card for debugging
                    print("Processing property card...")
                    
                    property_data = {
                        'scrape_date': datetime.now().strftime('%Y-%m-%d'),
                        'url': None,
                        'price': None,
                        'address': None,
                        'beds': None,
                        'baths': None,
                        'sqft': None
                    }
                    
                    # Try multiple possible selectors for each field
                    try:
                        property_data['url'] = card.find_element(By.CSS_SELECTOR, 'a[data-test="property-card-link"]').get_attribute('href')
                    except NoSuchElementException:
                        pass

                    try:
                        property_data['price'] = card.find_element(By.CSS_SELECTOR, '[data-test="property-card-price"]').text
                    except NoSuchElementException:
                        pass

                    try:
                        property_data['address'] = card.find_element(By.CSS_SELECTOR, '[data-test="property-card-addr"]').text
                    except NoSuchElementException:
                        pass

                    # Add the property data if we found at least some information
                    if any(value is not None for value in property_data.values()):
                        properties.append(property_data)
                        print(f"Successfully processed property: {property_data['address']}")
                    
                except Exception as e:
                    print(f"Error processing property card: {str(e)}")
                    continue
            
            return properties
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            return properties

    def save_to_csv(self, properties, filename):
        """Save scraped data to CSV file"""
        if not properties:
            print("No properties to save")
            return
            
        df = pd.DataFrame(properties)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def generate_market_report(self, properties):
        """Generate a basic market analysis report"""
        if not properties:
            return "No data available for analysis"
        
        # Convert price strings to numbers, handling various formats
        prices = []
        for p in properties:
            try:
                if p['price']:
                    # Remove '$' and ',' and convert to float
                    price_str = p['price'].replace('$', '').replace(',', '')
                    # Handle 'K' and 'M' suffixes
                    if 'K' in price_str:
                        price = float(price_str.replace('K', '')) * 1000
                    elif 'M' in price_str:
                        price = float(price_str.replace('M', '')) * 1000000
                    else:
                        price = float(price_str)
                    prices.append(price)
            except (ValueError, AttributeError):
                continue
        
        report = {
            'total_listings': len(properties),
            'properties_with_prices': len(prices),
            'average_price': round(sum(prices) / len(prices), 2) if prices else 0,
            'min_price': round(min(prices), 2) if prices else 0,
            'max_price': round(max(prices), 2) if prices else 0,
            'report_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        return report

    def cleanup(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    # Initialize scraper
    scraper = RealEstateScraper()
    scraper.setup_driver()
    
    try:
        # Example usage
        zip_code = "90210"  # Example zip code
        print(f"Starting scrape for zip code {zip_code}")
        
        # Scrape properties
        properties = scraper.scrape_zillow_listings(zip_code)
        
        if properties:
            # Save to CSV
            filename = f"real_estate_data_{zip_code}_{datetime.now().strftime('%Y%m%d')}.csv"
            scraper.save_to_csv(properties, filename)
            
            # Generate report
            report = scraper.generate_market_report(properties)
            print("\nMarket Report:")
            print(json.dumps(report, indent=2))
        else:
            print("No properties were found. Please check the script configuration.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()