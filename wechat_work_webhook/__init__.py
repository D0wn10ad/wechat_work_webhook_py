# https://work.weixin.qq.com/api/doc/90000/90136/91770

import requests
import base64
import uuid
import os
import hashlib
import pathlib
import logging

from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_not_exception_type

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s [%(threadName)s]")
logger = logging.getLogger(__name__)

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def POST(**kwargs):

        logger.debug(f"""{kwargs=}""")

        if kwargs.get("proxies") is not None:
            logger.debug(f"""{kwargs.get("proxies")=} is used for requests()""")

        return requests.post(**kwargs)
    
def connect(webhook_url):
    return WechatWorkWebhook(webhook_url)

class WechatWorkWebhook:
    headers = {"Content-Type": "application/json"}
    proxies = None
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def setProxy(self, p):
        if p is not None and type(p) == dict:

            self.proxies = p
            logger.debug(f"Setting Proxy using {p=} and {self.proxies=}")
            return True

        return False

    def text(self, text, mentioned_list=[], mentioned_mobile_list=[]):
        data = {
              "msgtype": "text",
              "text": {
                  "content": text,
                  "mentioned_list": mentioned_list,
                  "mentioned_mobile_list": mentioned_mobile_list
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()
    
    def markdown(self, markdown):
        data = {
              "msgtype": "markdown",
              "markdown": {
                  "content": markdown
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()

    def markdown_v2(self, markdown):
        data = {
              "msgtype": "markdown_v2",
              "markdown": {
                  "content": markdown
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()

    
    def image(self, image_path):
        with open(image_path, "rb") as image_file:
            image_base64 = str(base64.b64encode(image_file.read()), encoding='utf-8') 
        image_md5 = hashlib.md5(pathlib.Path(image_path).read_bytes()).hexdigest()

        data = {
              "msgtype": "image",
              "image": {
                 "base64": image_base64,
                 "md5": image_md5
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()
    
    def df(self, df):
        'convert df into image and upload'
        import dataframe_image
        
        image_path = "/tmp/dataframe_to_image_%s.png" % uuid.uuid1()
        dataframe_image.export(df, image_path)
        
        with open(image_path, "rb") as image_file:
            image_base64 = str(base64.b64encode(image_file.read()), encoding='utf-8') 
        image_md5 = hashlib.md5(pathlib.Path(image_path).read_bytes()).hexdigest()
        
        os.remove(image_path)

        data = {
              "msgtype": "image",
              "image": {
                 "base64": image_base64,
                 "md5": image_md5
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()
    
    def news(self, articles):
        data = {
              "msgtype": "news",
              "news": {
                  "articles": articles
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()

    def media(self, media_id):
        data = {
              "msgtype": "file",
              "file": {
                  "media_id": media_id
              }
           }

        return POST(url=self.webhook_url, headers=self.headers, json=data, proxies=self.proxies).json()
    
    def upload_media(self, file_path):
        upload_url = self.webhook_url.replace('send', 'upload_media') + '&type=file'

        return POST(upload_url, files=[('media', open(file_path, 'rb'))], proxies=self.proxies).json()  

    def file(self, file_path):
        media_id = self.upload_media(file_path)['media_id']
        return self.media(media_id)
