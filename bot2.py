import io
import os
import selenium
import time
import requests
import logging
# import numpy as np
import telegram
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
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import MessageFilter

trigger_phrases = [
    'where did my',
    'who moved my',
    'has anyone seen my',
    'where is my',
    'did someone take my',
    'did anyone see my'
]

class CommandFilter(MessageFilter):
    def filter(self, message):
        for item in trigger_phrases:
            if item in message.text.lower():
                return True
        return False

def main():
    # bot = telegram.Bot(token = '1472266836:AAHRgGYGogHlbfGUM9meOqs21zDGeQ6snKQ')
    
    options = Options()
    options.add_argument("--headless")
    
    global driver
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.PhantomJS()
    driver.get("https://images.google.com/")

    PORT = int(os.environ.get('PORT', 5000))
    TOKEN = '1472266836:AAHRgGYGogHlbfGUM9meOqs21zDGeQ6snKQ'
    
    global updater
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
                     
    commandfilter = CommandFilter()
    
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    stop_handler = CommandHandler('stop', stop)
    dispatcher.add_handler(stop_handler)
    
    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)
    
    custom_handler = MessageHandler(commandfilter, send_image)
    print(commandfilter)
    dispatcher.add_handler(custom_handler)
    
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook('https://hidden-bayou-20981.herokuapp.com/' + TOKEN)
    updater.idle()
    

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    
def send_image(update, context):
    commandtext = update.message.text
    username = update.message.from_user.first_name
    handle = update.message.from_user.username
    # imagename = ''
    
    for i in range(len(trigger_phrases)):
        commandtext = commandtext.replace(trigger_phrases[i], "")
    commandtext = commandtext.split()[0].replace(" ", "")
    print(commandtext)
    

    i = 0
    while True:
        if i == 2:
            break
        try:
            generateImage(commandtext, username, handle)
            break
        except Exception as e:
            print("Error:", e)
            i += 1
    
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('result.jpg','rb'))
    
def stop(update, context):
    exit()
    
    
def generateImage(imagename, username, handle):
    
    driver.get("https://images.google.com/")

    inputBox = driver.find_element_by_name("q")
    inputBox.send_keys(imagename)
    inputBox.send_keys(Keys.RETURN)

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@jsname="Q4LuWd"]')))
    images = driver.find_elements_by_xpath('//*[contains(@class, "Q4LuWd")]')
    print(len(images))

    image_url = ''
    found = 0

    for image in images:
        image.click()
        time.sleep(3)
        # actual_image = driver.find_elements_by_xpath('//*[@class="n3VNCb"]')
        actual_images = driver.find_elements_by_xpath('//*[@jsname="HiaYvf"]')
        for actual_image in actual_images:
            if 'http' in actual_image.get_attribute('src') and (('jpg' in actual_image.get_attribute('src')) or ('png' in actual_image.get_attribute('src'))) :
                print(actual_image.get_attribute('src'))
                image_url = actual_image.get_attribute('src')
                found = 1
                break
                
        if found == 1:
            break
            
    try:
        persist_image(imagename, image_url)
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
    if username is not None:
        draw.text(((bw-W)/2 + 50,(bh-H)/2 + 920), username, (0, 0, 0), font=font)
    elif handle is not None:
        draw.text(((bw-W)/2 + 50,(bh-H)/2 + 920), username, (0, 0, 0), font=font)
    
    back_im.save('result.jpg', quality=90)
    

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