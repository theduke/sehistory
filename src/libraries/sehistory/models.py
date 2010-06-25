'''
Created on 08.06.2010

@author: theduke
'''

from appengine_django.models import BaseModel
from google.appengine.ext import db

import re
import os
import sys

# Create your models here.


class SearchEngine(BaseModel):
    name = db.StringProperty(required=True, multiline=False)
    description = db.TextProperty()

class Domain(BaseModel):
    '''
    domain model 
    '''
    url = db.LinkProperty()
    country = db.StringProperty()
    searchEngine = db.ReferenceProperty(reference_class=SearchEngine)

class File(BaseModel):
    '''
    classdocs
    '''
    
    hash = db.StringProperty()
    data = db.BlobProperty()
    filename = db.StringProperty(multiline=False, required=True)
    description = db.StringProperty(multiline=False)
    extension = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)
    domains = db.ListProperty(item_type=db.Key)
    type = db.StringProperty(required=True, choices=('default', 'google-logo', 'bing-background'))
    uniqueFileName = db.StringProperty()
    
    @staticmethod
    def getOneByHash(hash):
        query = File.all()
        query.filter('hash =', hash);
        result = query.fetch(1)
        
        if (len(result)): return result[0]
        else: return None
        
    @staticmethod
    def getOneByUniqueFileName(filename):
        query = File.all()
        query.filter('uniqueFileName =', filename);
        result = query.fetch(1)
        
        if (len(result)): return result[0]
        else: return None
    
    def computeUniqueFilename(self):
        fileName = self.filename
        
        q = File.all().filter('filename =', fileName)
        if self.type: q.filter('type =', self.type)
        #namecounter will say how often the filename already exists
        nameCounter = q.count()
        
        # if we found something, calc new filename
        if nameCounter > 0:
            name, extension = os.path.splitext(fileName)
            fileName = name + '_' + nameCounter + extension
        
        self.uniqueFileName = fileName
    
    def getMimeType(self):
        mimes = {
                 'jpeg': 'image/jpeg',
                 'jpg':  'image/jpeg',
                 'gif':  'image/gif',
                 'png':  'image/png'
                }
        if not self.extension in mimes: raise Exception('Could not find mime type.')
        else: return mimes[self.extension]
            
class Crawl(BaseModel):
    type = db.StringProperty()
    success = db.BooleanProperty()
    body = db.TextProperty()
    headers = db.TextProperty()
    charset = db.StringProperty()
    date = db.DateTimeProperty()
    domain = db.ReferenceProperty(reference_class=Domain)
    files = db.StringListProperty()
