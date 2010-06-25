# Create your views here.
from django.http import HttpResponse

from libraries.sehistory.models import *

def index(request):
    return HttpResponse('TEEEEEEEST')

def file(request, fileName):
    f = File.getOneByUniqueFileName(fileName)
    
    if not f: return HttpResponse("This logo does not exist.")
    else: return HttpResponse(f.data, f.getMimeType());
    
    