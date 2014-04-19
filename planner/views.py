from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from models import PlanUser,PlanCourse
from fields import CappReportField
from utils import map_month_to_semester

from courses.models import Course,Department

from RPICappReport import *

def addCoursesTaken(request):
    if not request.user.is_authenticated():
        return HttpResponse("Please log in.")
    if request.method == 'POST':
        form = CappReportField(request.POST, request.FILES)
        if form.is_valid():

            capp_report_html = request.FILES['cappReportField'].read()
            courses_taken = RPICappReport.getCoursesTaken(capp_report_html)
            print_string = []
            first_term = min([course.term for course in courses_taken])
            plan_user = request.user.planuser
            plan_user.first_year = str(first_term)[:-2]
            plan_user.first_semester = map_month_to_semester(int(str(first_term[-2:])))
            plan_user.save()

            # Delete all previous records, if any exist
            PlanCourse.objects.filter(user=plan_user).delete()

            for x in courses_taken:
                if x.term == "Not Met" or len(x.term) != 6:
                    continue
                x.department_prefix = x.name.split(" ")[0]
                x.course_number = x.name.split(" ")[1]
                x.year = x.term[:-2]
                x.semester = map_month_to_semester(int(x.term[-2:]))
                department = Department.objects.get(code=x.department_prefix)
                new_plan_course = PlanCourse(
                    year=x.year, semester=x.semester,
                    user=request.user.planuser, department=department,
                    number=x.course_number
                )
                new_plan_course.save()
            return HttpResponseRedirect("/#/planner/");
    else:
        # if request.user.planuser.first_semester:
        #     return HttpResponse("You have already uploaded a capp report")
        form = CappReportField()
    return render_to_response('planner/upload_capp.html', {'form': form}, 
                                context_instance=RequestContext(request))
