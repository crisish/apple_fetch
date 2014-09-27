import json
from email.Message import Message
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import sys
import time
import logging
from email.mime.text import MIMEText
import smtplib
import os
import base64
import models

logging.basicConfig(level=logging.NOTSET,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='Apple_fetch.LOG',
                    filemode='w')
logger = logging.getLogger()

mailto_list=['130881221@qq.com', 'crisish@me.com', 'liminglei29@gmail.com'] 
#mailto_list=['130881221@qq.com', 'crisish@me.com'] 
mail_host="mail.crisish.com"
mail_port=25
mail_user="me" 
mail_pass="881221" 
mail_postfix="crisish.com"
  
def send_mail(to_list,sub,content):  
    me="iPhone"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:  
        server = smtplib.SMTP()  
        server.connect(mail_host, mail_port)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        logger.error('Something error during send email!') 
        raise Exception('Something error during send email!')
    return False  

class SaleQuery():
    def __init__(self, waitTime = 5):
        self.url = 'https://reserve.cdn-apple.com/HK/zh_HK/reserve/iPhone/availability.json'
        self.waitInterval = waitTime
        self.isAvailable = False
        self.models = models.MODELS 

    def fetchHtml(self):
        try:
            self.jsonFile =  'availability_' + str(int(time.time())) +'.json'
            cmd = 'wget -c ' + self.url + ' -O ' + self.jsonFile + ' -o wget.log'
            os.system(cmd)
        except Exception, e:
            logger.error('Get json file error!')
            raise Exception('Get json file error!')

    def loadJsonFile(self):
        try:
            self.sales = json.load(open(self.jsonFile, 'r'))
        except Exception, e:
            raise Exception('Something wrong during decode json file!' + str(e))

        if not len(self.sales):
            logger.error('It must be night because the page was closed by Apple!')
            raise Exception('It must be night because the page was closed by Apple!')

    def judgeSales(self):
        self.shops = {'R428': 'ifc', 'R409': 'CauseWay Bay', 'R485': 'Festival Walk'}
        self.availableModel = 'iPhone is COoooooooming!'
        shops = [shop for shop in self.sales if shop.startswith('R')]
        for shop in shops: 
            for model, isAvail in self.sales[shop].items():
                if isAvail and model in self.models:
                    logger.info('There has iPhone! Shop: ' + self.shops[shop] + ' Model: ' + self.models[model] +'!')
                    self.availableModel += '\nThere has iPhone! Shop: ' + self.shops[shop] + ' Model: ' + self.models[model] +'!'
                    self.isAvailable = True
                else:
                    logger.info('The model ' + model + ' is not for sale in this(' + self.shops[shop] + ') shop now!') 
            else:
                logger.info('There is no iPhone available in this('+ self.shops[shop] + ') shop!')
        else:
            logger.info('There is no iPhone available in any shop!')
            return False

    def cleanJsonFile(self):
        cmd = 'rm -rf ' + self.jsonFile
        try:
            os.system(cmd)
        except Exception, e:
            logger.error('Something error during clean jsonfile!')
            raise Exception('Something error during clean jsonfile!') 

    def startMoniter(self):
        while True:
            try:
                self.fetchHtml()
                # For test 
                #self.jsonFile = 'availability_1411553657.json'
                self.loadJsonFile()
                self.judgeSales()
                if self.isAvailable:
                    send_mail(mailto_list, 'iPhone is ready now!!!', self.availableModel)
                time.sleep(self.waitInterval)
            except Exception, e:
                logger.error('Something wrong in query iPhone sales! ' + str(e))
                send_mail(mailto_list, 'Something wrong in query iPhone sales!', str(e))
                return
            finally:
                self.cleanJsonFile()
                self.isAvailable = False

if __name__ == '__main__':
    M = SaleQuery(10)
    M.startMoniter()
