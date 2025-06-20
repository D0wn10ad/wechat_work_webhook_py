# https://work.weixin.qq.com/api/doc/90000/90136/91770

import requests
import base64
import uuid
import os
import hashlib
import pathlib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s [%(threadName)s]")
logger = logging.getLogger(__name__)

proxies = None

def setProxy(p):
	global proxies
	if p is not None and type(p) == dict:

		proxies = p
		logger.debug(f"Setting Proxy using {p=} and {proxies=}")
		return True
	return False

def POST(retry=5, retry_delay=5, silent=True, **kwargs):
#def POST(retry=5, retry_delay=5, silent=False, **kwargs):
	retried = 0
	while retried < retry:
		try:
			if proxies is None:
				logger.debug(f"{proxies=}, skipped for requests()")
				return requests.post(**kwargs)
			else:
				logger.debug(f"{proxies=} is used for requests()")
				return requests.post(proxies=proxies, **kwargs)
		except Exception as e:
			time.sleep(retry_delay)
			retried += 1
			if not silent:
				print(repr(e))
				print(traceback.format_exc())
				print(f"REQUEST FAILED FOR {retried} TIMES. RETRYING...")
				print(e)
	raise Exception('DOWNLOAD FAILED')
    
def connect(webhook_url):
    return WechatWorkWebhook(webhook_url)

class WechatWorkWebhook:
#    headers = {"Content-Type": "text/plain"}
    headers = {"Content-Type": "application/json"}
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        
    def text(self, text, mentioned_list=[], mentioned_mobile_list=[]):
        data = {
              "msgtype": "text",
              "text": {
                  "content": text,
                  "mentioned_list": mentioned_list,
                  "mentioned_mobile_list": mentioned_mobile_list
              }
           }
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()
    
    def markdown(self, markdown):
        data = {
              "msgtype": "markdown",
              "markdown": {
                  "content": markdown
              }
           }
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()

    def markdown_v2(self, markdown):
        data = {
              "msgtype": "markdown_v2",
              "markdown": {
                  "content": markdown
              }
           }
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()

    
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
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()
    
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
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()
    
    def news(self, articles):
        data = {
              "msgtype": "news",
              "news": {
                  "articles": articles
              }
           }
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()

    def media(self, media_id):
        data = {
              "msgtype": "file",
              "file": {
                  "media_id": media_id
              }
           }
#        return requests.post(self.webhook_url, headers=self.headers, json=data).json()
        return POST(self.webhook_url, headers=self.headers, json=data).json()
    
    def upload_media(self, file_path):
        upload_url = self.webhook_url.replace('send', 'upload_media') + '&type=file'

#        return requests.post(upload_url, files=[('media', open(file_path, 'rb'))]).json()
        return POST(upload_url, files=[('media', open(file_path, 'rb'))]).json()  

    def file(self, file_path):
        media_id = self.upload_media(file_path)['media_id']
        return self.media(media_id)
