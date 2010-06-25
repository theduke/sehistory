# Create your views here.
from django.http import HttpResponse

from libraries.sehistory import *

def weekly(request):
    # Google stuff
    g = Google()
    
    # check for new domains
    g.crawlForDomains()
    
    return HttpResponse("Parsed Domain List for new domains.")
    

def threedaily(request):
    # Google stuff
    g = Google()
    
    g.crawlAllDomains()
    # check for new domains
    
    b = Bing()
    b.crawlAllDomains()
    
    return HttpResponse("Parsed all Domains for new logos.")