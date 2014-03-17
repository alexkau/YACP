from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from models import PlanUser
from fields import CappReportField

from RPICappReport import *

def addCoursesTaken(request):
    # Handle file upload
    if request.method == 'POST':
        form = CappReportField(request.POST, request.FILES)
        if form.is_valid():
            capp_report_html = request.FILES['cappReportField'].read()
            courses_taken= RPICappReport.getCoursesTaken(capp_report_html)
            return HttpResponse(', '.join(courses_taken))
    else:
        form = CappReportField() # A empty, unbound form
    return render_to_response('planner/upload_capp.html', {'form': form}, context_instance=RequestContext(request))
