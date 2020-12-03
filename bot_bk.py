import io
import os
import selenium
import time
import requests
import numpy as np
from google_images_download import google_images_download
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def main():

    imagename = input("Enter image to overlay: ")
    username = input("Enter username: ")
    
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get("https://images.google.com/")

    inputBox = driver.find_element_by_name("q")
    inputBox.send_keys(imagename)
    inputBox.send_keys(Keys.RETURN)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@jsname="Q4LuWd"]')))
    images = driver.find_elements_by_xpath('//*[contains(@class, "Q4LuWd")]')
    print(len(images))

    image_url = ''

    for image in images:
        image.click()
        time.sleep(3)
        # actual_image = driver.find_elements_by_xpath('//*[@class="n3VNCb"]')
        actual_images = driver.find_elements_by_xpath('//*[@jsname="HiaYvf"]')
        for actual_image in actual_images:
            if 'http' in actual_image.get_attribute('src'):
                print(actual_image.get_attribute('src'))
                image_url = actual_image.get_attribute('src')
                break
        try:
            persist_image(imagename, image_url)
            break
        except:
            pass
    
    img = Image.open("template.jpg")
    jpg = 0
    try:
        overlay = Image.open(imagename + ".png")
    except:
        overlay = Image.open(imagename + ".jpg")
        jpg = 1
    
    w, h = overlay.size
    bw, bh = img.size
    
    if w < h:
        overlay = overlay.crop((0, (h - w)/2, w, (w + h)/2))
    elif w > h:
        overlay = overlay.crop(((w - h)/2, 0, (w + h)/2, h))
        
    overlay = overlay.resize((350, 350))
    
    back_im = img.copy()
    if jpg:
        back_im.paste(overlay, (630, 770))
    else:
        back_im.paste(overlay, (630, 770), overlay)
    
    draw = ImageDraw.Draw(back_im)
    font = ImageFont.truetype("comicsans.ttf", 250)
    W, H = font.getsize(imagename)
    draw.text(((bw-W)/2,(bh-H)/2 + 560), imagename, (255, 0, 0), font=font)
    draw.text(((bw-W)/2 + 100,(bh-H)/2 + 920), username, (0, 0, 0), font=font)
    
    back_im.save('result.jpg', quality=90)

    driver.close()



def persist_image(imagename, url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(imagename + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")
        

if __name__ == "__main__":
    main()
