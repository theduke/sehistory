from frontend.models import *

from libraries.BeautifulSoup import BeautifulSoup

import logging
import re
import urllib2
import hashlib
import datetime

import sys

class Crawler(object):
    def crawl(self, domain):
        
        crawl = Crawl(
          domain = domain,
          date = datetime.datetime.now()
        )
        
        request = urllib2.Request(url = domain.url,
        headers={
          'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.0; de; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
        });
        
        try:
            url = urllib2.urlopen(request)
        except:
            crawl.success = False
            return crawl
        
        html = url.read()
        
        info = url.info();
        ignore, charset = info['Content-Type'].split('charset=')
        
        html = html.decode(charset)
        
        crawl.body = html
        crawl.info = info
        crawl.charset = charset
        
        crawl.put()
        return crawl
    
    def crawlFile(self, url, type, description, domain):
        try:
            response = urllib2.urlopen(url)
        except:
            return False
        
        data = response.read()
        
        hash = hashlib.sha256(data).hexdigest()
        
        file = File.getOneByHash(hash)
        
        if not file:
        # file is not yet in database, so insert it
            filename = re.search(r'[a-zA-Z0-9\.\-_]+$', url).group(0)
            extension = re.search(r'(?<=\.)[\S]{3}$', filename).group(0)
            
            q = File.all()
            q.filter('filename =', filename).filter('extension =', extension)
            
            version = q.count()+1
        
            file = File(hash=hash, 
                        data=data , 
                        filename = filename,
                        extension = extension,
                        description = description,
                        type = type
                        )
            file.domains.append(domain.key())
            file.computeUniqueFilename()
  
            file.put()
        else:
            #file does already exist, check if domain is already in urls property
            if not domain.key() in file.domains:
                #domain is not yet in list, add it
                file.domains.append(domain.key())
                file.put()
                
        return file

class Bing(object):
    def parseForBackground(self, crawl):
        
        url = re.search(r'(?<=\;g\_img\=\{url\:\').*(?=\'\,id)', crawl.body).group(0)
        if not url: return False
        
        url = url.replace('\\', '')
        
        url = crawl.domain.url + url
        
        return url
    
    def crawlAllDomains(self):
        se = self.getSearchEngineObject()
        if not se: raise Exception('Could not find Bing SearchEngine')
        
        domains = db.Query(Domain).filter('searchEngine =', se).fetch(99999999)
        
        for domain in domains:
            c = Crawler()
            
            # crawl the domain, retrieve the crawl object with html response
            crawl = c.crawl(domain)
            # if the crawl failed, skip to next domain
            if not crawl: continue
            
            # extract url and description for logo from html
            picUrl = self.parseForBackground(crawl)
            
            # if no logo can be found, continue
            if not picUrl: continue
            
            
            file = c.crawlFile(picUrl, 'bing-background', '', domain)
    
    def getSearchEngineObject(self):
        result = db.Query(SearchEngine).filter('name =', 'Bing').fetch(1)
        
        # if the SearchEngine object does not exist yet in the db
        # create it
        if not len(result):
            bing = SearchEngine(name = 'Bing')
            bing.put()
            
            domain = Domain(url='http://www.bing.com', searchEngine=bing)
            domain.put()
        else: bing = result[0]
        
        return bing

class Google(object):
    def parseForLogo(self, crawl):
        
        info = Google.extractLogo(self, crawl.body)
        pic = info[0]
        
        # return false if the pic could not be found
        if not pic: 
            return False
        
        url = crawl.domain.url + pic
        
        return {'pic': pic, 'description': info[1], 'url': url}
    
    def extractLogo(self, html):
        soup = BeautifulSoup(html)
    
        img = soup.find('img', id='logo')
        div = soup.find('div', id='logo')
        
        description = ''
        
        if img:
            pic = img['src']
            if 'title' in img: description = img['title']
        elif div:
            pic = re.search(r'(?<=url\()\S+(?=\))', str(div)).group(0)
        else:
            msg = 'Cronjob: Logos: could not find IMG or DIV tag with logo id!'
            logging.error(msg)
            print msg
            return False
        
        #pic = pic.decode(charset)
        return [pic, description]
    
    def crawlAllDomains(self):
        se = self.getSearchEngineObject()
        if not se: raise Exception('Could not find Google SearchEngine')
        
        domains = db.Query(Domain).filter('searchEngine =', se).fetch(99999999)
        
        for domain in domains:
            try: 
                c = Crawler()
                
                # crawl the domain, retrieve the crawl object with html response
                crawl = c.crawl(domain)
                # if the crawl failed, skip to next domain
                if not crawl: continue
                
                # extract url and description for logo from html
                info = self.parseForLogo(crawl)
                
                # if no logo can be found, continue
                if not info: continue
                
                file = c.crawlFile(info['url'], 'google-logo', info['description'], domain)
            except Exception as e:
                logging.error("Error while crawling Google domain " + crawl.domain.url + ": " + str(e))
            
    def crawlForDomains(self):
        # get google searchengine
        se = self.getSearchEngineObject()
        
        # fetch html from google domain list
        url = urllib2.urlopen('http://www.google.com/language_tools')
        html = url.read()
        
        info = url.info();
        ignore, charset = info['Content-Type'].split('charset=')
        
        # decode with proper charset
        html = html.decode(charset)
        
        # parse html for all domains
        domains = re.findall('www.google.[a-z]+<br>\S+(?=</a>)', html)
        
        for d in domains:
            url, country = d.split('<br>')
            url = 'http://' + url
            
            q = Domain.all();
            q.filter('url =', url).order('url')
            r = q.fetch(1)
            
            if len(r)==0:
                m = Domain(url = url, country = unicode( country ), searchEngine = se )
                m.put()
    
    def getSearchEngineObject(self):
        result = db.Query(SearchEngine).filter('name =', 'Google').fetch(1)
        
        # if the SearchEngine object does not exist yet in the db
        # create it
        if not len(result):
            goog = SearchEngine(name = 'Google')
            goog.put()
        else: goog = result[0]
        
        return goog