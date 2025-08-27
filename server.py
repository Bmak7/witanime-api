import os
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def fetch_video_list_witanime(episode_url):
    video_list = []
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('log-level=3')

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(episode_url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#episode-servers a.server-link")))
        servers = driver.find_elements(By.CSS_SELECTOR, "ul#episode-servers a.server-link")

        for i in range(len(servers)):
            try:
                servers = driver.find_elements(By.CSS_SELECTOR, "ul#episode-servers a.server-link")
                el = servers[i]
                name = el.text.strip() or f"Server {i+1}"
                driver.execute_script("arguments[0].click();", el)

                iframe_el = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#iframe-container iframe[src]"))
                )
                url = iframe_el.get_attribute("src")
                if url:
                    video_list.append({"server": name, "url": url})
            except Exception:
                continue
    finally:
        driver.quit()

    return video_list

@app.route("/get_servers", methods=["GET"])
def get_servers():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url="}), 400
    return jsonify(fetch_video_list_witanime(url))

@app.route("/")
def root():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
