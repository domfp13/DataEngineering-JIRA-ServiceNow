# -*- coding: utf-8 -*-
# Luis Enrique Fuentes Plata
# Daniel Steinemann
# Angel Angel

from typing import Optional
from main import JiraServiceNow

class Request:
    args = dict()

    def __init__(self, type:str):
        self.args['message'] = type

request = Request('args')

JiraServiceNow(request)