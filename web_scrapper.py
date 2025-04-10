import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---- CONFIG ----
BASE = "https://lovegrown-diamonds.com"
COLLECTIONS = [
    "/collections/earrings",
    "/collections/bracelets",
    "/collections/rings",
    "/collections/necklaces",
    "/collections/pendants"
]
FOLDER_IMAGES = "all_jewelry_media/images"
FOLDER_VIDEOS = "all_jewelry_media/videos"
os.makedirs(FOLDER_IMAGES, exist_ok=True)
os.makedirs(FOLDER_VIDEOS, exist_ok=True)

# ---- SELENIUM SETUP ----
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

image_count = 0
video_count = 0

def download_file(url, folder, filename):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        path = os.path.join(folder, filename)
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return path
    except Exception as e:
        print(f"⚠️ Error downloading {url} – {e}")
        return None

for path in COLLECTIONS:
    full_url = urljoin(BASE, path)
    print(f"\n🔎 Visiting: {full_url}")
    driver.get(full_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # ---- IMAGES ----
    image_tags = soup.find_all("img")
    print(f"🖼️ Found {len(image_tags)} images")

    for img in image_tags:
        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        if any(x in src.lower() for x in ["logo", "icon", "avatar", "hand", "ear", "person", "model", "lifestyle"]):
            continue

        img_url = urljoin(BASE, src)
        if img_url.startswith("data:"):
            continue

        try:
            r = requests.get(img_url, stream=True)
            r.raise_for_status()
            image = Image.open(BytesIO(r.content))
            if image.mode != "RGB":
                image = image.convert("RGB")
            if image.width < 300 or image.height < 300:
                continue
            image_count += 1
            filename = f"jewel_{image_count}.png"
            image.save(os.path.join(FOLDER_IMAGES, filename))
            print(f"✅ Saved image: {filename}")
        except Exception as e:
            print(f"⚠️ Failed image: {img_url} – {e}")

    # ---- VIDEOS ----
    video_tags = soup.find_all("video")
    print(f"🎥 Found {len(video_tags)} video tags")

    for vid in video_tags:
        sources = vid.find_all("source")
        for source in sources:
            vid_src = source.get("src")
            if not vid_src:
                continue
            vid_url = urljoin(BASE, vid_src)
            video_count += 1
            filename = f"jewel_{video_count}.mp4"
            saved = download_file(vid_url, FOLDER_VIDEOS, filename)
            if saved:
                print(f"✅ Saved video: {filename}")

driver.quit()
print(f"\n🎉 All done! {image_count} images and {video_count} videos saved in 'all_jewelry_media/'")
