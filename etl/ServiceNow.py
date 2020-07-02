# -*- coding: utf-8 -*-
# Luis Enrique Fuentes Plata
# Daniel Steinemann
# Angel Angel

from typing import Optional
import requests
from bs4 import BeautifulSoup as BS4
from etl.GeneralFunctions import getUserName, getPassword

class ServiceNowSession:
  # Class variable
  instance = None
  __snow_url = 'https://iaas.service-now.com/navpage.do'
  __login_url = 'https://iaas.service-now.com/login.do'

  @staticmethod
  def getInstance(registry:dict):
    """ Missing docstring
    """
    if ServiceNowSession.instance == None:
      ServiceNowSession(registry)
    return ServiceNowSession.instance
  
  def __init__(self, registry:dict):
    """ Virtually private constructor, missing docstring
    """
    if ServiceNowSession.instance != None:
      raise Exception("This is a singleton object")
    else:
      session = requests.session()
      request = session.get(ServiceNowSession.__snow_url)
      auth_payload = registry
      request_1 = session.post(ServiceNowSession.__login_url, data=auth_payload)
      soup = BS4(request_1.text, 'html.parser')
      if 'Establishing session' in soup.find_all("h1", class_="loading-message")[0]:
        ServiceNowSession.instance = session
      else:
        ServiceNowSession.instance = None
  
class SessionHandler:
  def __init__(self):
    self.__registry =  {
      "user_name": getUserName(), 
      "user_password": getPassword(),
      "ni.nolog.user_password": "true",
      "ni.noecho.user_name": "true",
      "ni.noecho.user_password": "true",
      "language_select": "en",
      "screensize": "1536x864",
      "sys_action": "sysverb_login",
      "sysparm_login_url": "welcome.do"
    }
    self.instance = ServiceNowSession.getInstance(self.__registry)
