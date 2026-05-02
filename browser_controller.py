from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from core.error_logger import log_error
from core.error_handler import handle_error
from core.recovery_engine import recover

driver = None

def get_brave_path():
    paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def get_driver():
    global driver
    if driver is not None:
        try:
            # Check if any windows are open and if the driver is responsive
            if not driver.window_handles:
                driver = None
            else:
                _ = driver.title
                return driver
        except:
            driver = None

    brave_path = get_brave_path()
    
    options = Options()
    if brave_path:
        options.binary_location = brave_path
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())

    try:
        # Try with user profile first
        profile_options = Options()
        if brave_path:
            profile_options.binary_location = brave_path
        profile_options.add_argument(r"--user-data-dir=C:\Users\LENOVO\AppData\Local\BraveSoftware\Brave-Browser\User Data")
        profile_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        profile_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(service=service, options=profile_options)
    except Exception as e:
        print("Profile locked or not found, opening without profile...")
        # Fallback to without profile
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    return driver

def open_youtube_and_play(command_query):
    global driver
    
    # 1. Fetch or reinitialize driver
    driver = get_driver()

    # 2. Safely navigate to YouTube (handles NoSuchWindowException)
    try:
        driver.get("https://www.youtube.com")
    except Exception:
        print("Driver state invalid. Reinitializing...")
        driver = None
        driver = get_driver()
        driver.get("https://www.youtube.com")

    import re
    query = re.sub(r'\b(play|start|resume|gana|song|music|on youtube)\b', '', command_query, flags=re.IGNORECASE).strip()

    if query != "":
        search = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search.clear()
        search.send_keys(query)
        search.send_keys(Keys.RETURN)
        
        # Search results use a#video-title
        video_selector = "a#video-title"
    else:
        # Homepage uses a#video-title-link
        video_selector = "a#video-title-link, a#video-title"

    def click_video():
        # Wait for video results to appear
        video = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, video_selector))
        )
        
        href = video.get_attribute("href")
        if href:
            driver.get(href)
        else:
            # Fallback to click if href is somehow not ready
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, video_selector))
            ).click()

        time.sleep(2)
        try:
            is_paused = driver.execute_script("return document.querySelector('video').paused;")
            if is_paused:
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys("k")
        except:
            pass

    try:
        click_video()
    except Exception as e:
        log_error(e, context="video_click_logic")
        err_type = handle_error(e)
        
        def retry_action():
            global driver
            if err_type == "DRIVER_DISCONNECTED":
                driver = get_driver()
                driver.get("https://www.youtube.com")
                if query != "":
                    search = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.NAME, "search_query"))
                    )
                    search.clear()
                    search.send_keys(query)
                    search.send_keys(Keys.RETURN)
            click_video()
            
        recover(err_type, retry_action, restart_func=close_browser, init_func=get_driver)

def focus_player():
    driver = get_driver()
    try:
        player = driver.find_element(By.CSS_SELECTOR, "#movie_player")
        player.click()
    except:
        pass

def pause_video():
    driver = get_driver()
    try:
        driver.execute_script("document.querySelector('video').pause();")
    except:
        pass

def resume_video():
    driver = get_driver()
    try:
        driver.execute_script("document.querySelector('video').play();")
    except:
        pass

def close_video():
    driver = get_driver()
    driver.back()

def close_browser():
    global driver
    if driver:
        driver.quit()
        driver = None

def play_next():
    driver = get_driver()
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.SHIFT, "n")

def volume_up():
    driver = get_driver()
    try:
        driver.execute_script("let v = document.querySelector('video'); if(v) v.volume = Math.min(1.0, v.volume + 0.05);")
    except:
        pass

def volume_down():
    driver = get_driver()
    try:
        driver.execute_script("let v = document.querySelector('video'); if(v) v.volume = Math.max(0.0, v.volume - 0.05);")
    except:
        pass

def play_previous():
    driver = get_driver()
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.SHIFT, "p")

def maximize_window():
    driver = get_driver()
    driver.maximize_window()

def minimize_window():
    driver = get_driver()
    driver.minimize_window()
