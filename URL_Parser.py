# -*- coding: utf-8 -*-
"""
Created on Sun Jul 02 15:32:37 2017

@author: MITCHELL.FYOCK
"""

import os, sys, urllib2
from bs4 import BeautifulSoup

url = 'http://www.historycolorado.org/connect/office-archaeology-historic-preservation'

content = urllib2.urlopen(url).read()
soup = BeautifulSoup(content, 'lxml')

print(soup.title)