import io
import os
import selenium
import time
import requests
import logging
import numpy as np
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


class CommandFilter(MessageFilter):
    def filter(self, message):
        trigger_phrases = [
            'where did my',
            'who moved my',
            'has anyone seen my',
            'where is my',
            'did someone take my'
        ]
        for item in trigger_phrases:
            if item in message.text.lower():
                return True
        return False

def main():
    # bot = telegram.Bot(token = '1472266836:AAHRgGYGogHlbfGUM9meOqs21zDGeQ6snKQ')
    global updater
    updater = Updater(token = '1472266836:AAHRgGYGogHlbfGUM9meOqs21zDGeQ6snKQ', use_context=True)
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
    
    updater.start_polling()
    

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    
def send_image(update, context):
    commandtext = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text=commandtext)
    
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('result.jpg','rb'))
    
def stop(update, context):
    exit()
    
    
if __name__ == "__main__":
    main()