from numpy import log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import redis 
import logging
logger = logging.getLogger(__name__)

r = redis.Redis(host='localhost', port=7777)

PROFILE_PAGE = "https://www.linkedin.com/in/collin-wischmeyer-b55659a4/"

def complete_captcha_if_needed(driver, wait):
    try:
        # Check for captcha, solve if recaptcha
        iframe1 = wait_for(driver, By.ID, "captcha-internal", timeout=3)
    except TimeoutException as e:
        logger.warning(f"No captcha found, assuming no captcha is required")
        iframe1 = None
    
    if iframe1 is not None:
        try:
            time.sleep(2)
            driver.switch_to.frame(iframe1)
            iframe2 = driver.find_element(By.XPATH, "//iframe[contains(@title,'reCAPTCHA')]")
            driver.switch_to.frame(iframe2)
            captcha_box = driver.find_element(By.ID, 'recaptcha-anchor')
            captcha_box.click()
        except NoSuchElementException as e:
            logger.warning(f"Captcha found, error solving: {e}")
            logger.warning(f"Sleeping for 10 seconds")
            logger.warning(f"Solve manually and type c, then press enter to continue")
            time.sleep(10)

    # I dont have the name of the iframe that is used for 
    #  the secondary captcha (the gridded pictures) that sometimes shows up
    #  but the idea is to pause long enough to allow for a manual solve of that as well 
    return
        

# TODO: Context manager for driver and wait
def linkedin_login(driver, email, password):
    # Go to LinkedIn login page
    driver.get("https://www.linkedin.com/login")

    # Enter email
    email_input = wait_for(driver, By.ID, "username")
    email_input.clear()
    email_input.send_keys(email)

    # Enter password
    password_input = driver.find_element(By.ID, "password")
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    complete_captcha_if_needed(driver)
    return driver

# def collect_profile_data(driver, wait):
#     profile_card = driver.find_element(By.TAG_NAME, "section").get_attribute('data-member-id')

def wait_for(driver,  by, value, timeout=10):
    wait = WebDriverWait(driver, timeout=timeout)
    try:
        element =wait.until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        logger.warning(f"Element {value} not found")
        return None

def get_profile_section(driver, section_name, tab_xpath=None ):
    "Get a specific card on a profile page, and the company tab within that card"
    # Get interest section
    wait_for(driver, By.ID, section_name)
    interest_card = driver.find_element( By.ID,section_name).find_element(By.XPATH,"..")
    # Unhide companies content
    if tab_xpath is not None:
        companies_btn = interest_card.find_element(By.XPATH, tab_xpath)
        companies_btn.click()
    return interest_card

def scroll_and_act(driver, action, wait_time=2, *args, **kwargs):
    # Scroll to load all companies
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        action(*args, **kwargs)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)   
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return args, kwargs

def get_company_elements(driver, total_links,*args, **kwargs):
    
    breakpoint()
    company_a = driver.find_elements(By.XPATH, "//li[contains(@class,'pvs-list__item--one-column')]/a")
    # Class is active_tab_companies_interests FWIW
    name = driver.find_element(By.XPATH,"//span").text
    company_a 
    for a in company_a:
        company_links = [a.get_attribute('href') for a in company_a]
        r.sadd('company_links', *company_links)
        total_links.extend(company_links)

def get_company_links_by_css(driver, total_links,*args, **kwargs):
    companies = []
    company_elements = driver.find_elements(By.CSS_SELECTOR, "ul.reusable-search__entity-result-list li")
    for elem in company_elements:
        try:
            name_elem = elem.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a span[aria-hidden='true']")
            link_elem = elem.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
            company_name = name_elem.text.strip()
            company_url = link_elem.get_attribute("href")
            companies.append({"name": company_name, "url": company_url})
        except Exception as e:
            print(f"Error getting company link by css: {e}")
            continue
        return companies

def follow_company(driver, company_id):
    driver.get(f'https://www.linkedin.com/company/{company_id}')
    follow_btn = wait_for(driver, By.CLASS_NAME,"follow")
    follow_btn.click()
    
    try: # we could just load the next page, but we want to emulate a human user
        dismiss_popup = wait_for(driver, By.XPATH, "//button[contains(@aria-label,'Dismiss')]")
        dismiss_popup.click()
    except TimeoutException:
        print(f"No dismiss popup found for company {company_id}")
        pass
    return

def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def linkedin_login_and_get_followed_companies(email, password, headless=True):
    driver = init_driver(headless)

    try:
        driver = linkedin_login(driver, email, password)

        # Wait for page to load
        wait_for(driver, By.CLASS_NAME, "profile-card")
        profile_card = driver.find_element(By.CLASS_NAME, "profile-card")
        profile_url = profile_card.find_element(By.XPATH, "//a[contains(@href,'/in/')]").get_attribute('href')
        driver.get(profile_url)

        # Get interest section
        companies_btn = get_profile_section(driver, "interests", "//button/span[contains(text(),'Companies')]/..")
        companies_btn.click()
        # Click on the "See All Companies" link
        companies_href_class = "navigation-index-see-all-companies"
        companies_link = companies_btn.find_element(By.ID,companies_href_class).get_attribute('href')
        companies_link.click()
        
        driver.get(companies_link)
        _ = wait_for(driver, By.ID, "scaffold-finite-scroll__content")
        
        # Extract followed companies
        # company_links_by_css = scroll_and_act(driver, get_company_links_by_css, total_links=[])
        company_links = scroll_and_act(driver, get_company_elements, total_links=[])

        return companies

    finally:
        driver.quit()

if __name__ == "__main__":
    companies = linkedin_login_and_get_followed_companies(os.getenv("LINKEDIN_USERNAME"), os.getenv("LINKEDIN_PASSWORD"), headless=False)
    for company in companies:
        print(company["name"], company["url"])
