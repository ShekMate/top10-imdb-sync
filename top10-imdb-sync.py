import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# IMDb Credentials (Replace with your actual login)
IMDB_USERNAME = "YOUR_USERNAME/EMAIL"
IMDB_PASSWORD = "YOUR_PASSWORD"
IMDB_LIST_URL = "YOUR_IMDB_LIST_URL"

# TMDb API Key (Replace with your key)
TMDB_API_KEY = "YOUR TMDB_API_KEY"

# Function to get IMDb ID from TMDb API
def get_imdb_id(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title.replace(' ', '%20')}&api_key={TMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        movie_id = data["results"][0]["id"]
        imdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}/external_ids?api_key={TMDB_API_KEY}"
        imdb_response = requests.get(imdb_url)
        imdb_data = imdb_response.json()
        return imdb_data.get("imdb_id", None)

    return None

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Add a real user-agent to bypass IMDb bot detection
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Ensure the screenshots directory exists
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# Step 1: Check if Already Logged into IMDb
driver.get("https://www.imdb.com/")
time.sleep(5)

try:
    profile_icon = driver.find_element(By.XPATH, "//div[contains(@class, 'ipc-btn__text')]")
    print("✅ Already logged into IMDb. Proceeding...")
except:
    print("🔐 Logging into IMDb...")
    driver.get("https://www.imdb.com/registration/signin")

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Sign in with IMDb']"))).click()
        time.sleep(3)
        driver.find_element(By.ID, "ap_email").send_keys(IMDB_USERNAME)
        driver.find_element(By.ID, "ap_password").send_keys(IMDB_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
        time.sleep(5)
        print("✅ Successfully logged into IMDb.")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.quit()
        exit()

# Step 2: Scrape Existing IMDb List
print("📄 Fetching existing IMDb list...")
driver.get(IMDB_LIST_URL)
time.sleep(5)

existing_movies = {}
movie_elements = driver.find_elements(By.XPATH, "//h3[@class='ipc-title__text']")
for movie in movie_elements:
    try:
        # Get the parent container of the movie title and then navigate to the link
        link = movie.find_element(By.XPATH, "./ancestor::li//a[@class='ipc-title-link-wrapper']")
        movie_title = movie.text.strip()
        imdb_id = link.get_attribute("href").split("/")[4]  # Extract IMDb ID from URL
        existing_movies[movie_title] = imdb_id
    except Exception as e:
        print(f"⚠️ Error processing movie: {movie.text}. Error: {e}")

print(f"🎥 IMDb List currently has {len(existing_movies)} movies.")
print(f"Current IMDb List: {existing_movies}")

# Step 3: Scrape FlixPatrol Top 10 Movies
print("🍿 Fetching FlixPatrol Top 10 Movies...")
driver.get("https://flixpatrol.com/top10/netflix/united-states/")
time.sleep(5)

# Scroll to TOP 10 Movies section
movies_section = driver.find_element(By.XPATH, "//h3[contains(text(),'TOP 10 Movies')]")
driver.execute_script("arguments[0].scrollIntoView(true);", movies_section)
time.sleep(2)

try:
    # Scrape Top 10 Movie Titles from FlixPatrol
    movies = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
        (By.XPATH, "//h3[contains(text(),'TOP 10 Movies')]/ancestor::div[contains(@class, 'grid-cols-4')]/following-sibling::div//td[@class='table-td']/a")
    ))
    flixpatrol_movies = [movie.text.strip() for movie in movies if movie.text.strip()]
    
    if not flixpatrol_movies:
        raise Exception("No movies found on the FlixPatrol page.")
    
    print("🔍 Top 10 Movies from FlixPatrol:")
    for index, title in enumerate(flixpatrol_movies[:10], start=1):
        print(f"{index}. {title}")

    # Get IMDb IDs for FlixPatrol Top 10
    flixpatrol_imdb_ids = {}
    for movie in flixpatrol_movies:
        imdb_id = get_imdb_id(movie)
        if imdb_id:
            flixpatrol_imdb_ids[movie] = imdb_id

    print(f"🔍 Found {len(flixpatrol_imdb_ids)} matching IMDb IDs.")
    print(f"FlixPatrol Top 10 IMDb IDs: {flixpatrol_imdb_ids}")

except Exception as e:
    print(f"⚠️ Error extracting FlixPatrol movie titles: {e}")
    flixpatrol_movies = []

# Step 4: Compare IMDb List with Netflix Top 10
to_remove = {title: imdb_id for title, imdb_id in existing_movies.items() if imdb_id not in flixpatrol_imdb_ids.values()}
to_add = {title: imdb_id for title, imdb_id in flixpatrol_imdb_ids.items() if imdb_id not in existing_movies.values()}

print(f"❌ Movies to REMOVE: {to_remove}")
print(f"✅ Movies to ADD: {to_add}")

# Step 5: Remove Movies from IMDb List
for title, imdb_id in to_remove.items():
    print(f"❌ Removing: {title} ({imdb_id})")
    driver.get(f"https://www.imdb.com/title/{imdb_id}/?ref_=nv_sr_srsg")
    time.sleep(5)

    try:
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-testid='tm-box-addtolist-button']"))
        )
        driver.execute_script("arguments[0].click();", dropdown_button)
        time.sleep(2)

        # Unselect from Netflix Top 10 Movies (USA)
        remove_from_list_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/ul/div[1]/div"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", remove_from_list_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", remove_from_list_button)
        time.sleep(2)

        print(f"✅ Successfully removed: {title}")
    except Exception as e:
        print(f"⚠️ Failed to remove {title}: {e}")

# Step 6: Add New Movies to IMDb List
for title, imdb_id in to_add.items():
    print(f"✅ Adding: {title} ({imdb_id})")
    driver.get(f"https://www.imdb.com/title/{imdb_id}/?ref_=nv_sr_srsg")
    time.sleep(5)

    try:
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-testid='tm-box-addtolist-button']"))
        )
        driver.execute_script("arguments[0].click();", dropdown_button)
        time.sleep(2)

        add_to_list_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div/div[2]/ul/div[1]/div"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", add_to_list_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", add_to_list_button)
        time.sleep(2)

        print(f"✅ Successfully added: {title}")
    except Exception as e:
        print(f"⚠️ Failed to add {title}: {e}")

print("✅ IMDb List Updated!")
driver.quit()
