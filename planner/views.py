from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from models import PlanUser
from fields import CappReportField

from RPICappReport import *

def addCoursesTaken(request):
    if request.method == 'POST':
        form = CappReportField(request.POST, request.FILES)
        if form.is_valid():
            capp_report_html = request.FILES['cappReportField'].read()
            courses_taken = RPICappReport.getCoursesTaken(capp_report_html)
            print_string = []
            for x in courses_taken:
                print_string.append(x.name + " : " + x.term + ", ")  
            return HttpResponse(print_string)
    else:
        form = CappReportField() 
    return render_to_response('planner/upload_capp.html', {'form': form}, context_instance=RequestContext(request))
