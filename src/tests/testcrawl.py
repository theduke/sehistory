from libraries.sehistory import Google
import urllib2

request = urllib2.Request(url = 'http://www.google.com',
headers={
  'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.0; de; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
});
        
response = urllib2.urlopen(request)
html = response.read()

goog = Google()

info = goog.extractLogo(html, 'UTF-8')
print info[0]
print info[1]