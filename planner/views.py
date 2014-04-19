from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from models import PlanUser,PlanCourse
from fields import CappReportField
from utils import map_month_to_semester

from courses.models import Course,Department,Section

from decimal import *

from RPICappReport import *
from RPIRateMyProfessors import *

def getDifficulty(season, course_number, dept_code):
    try:
        sections = Section.objects.filter(semester__name__startswith=season,  course__number=course_number, course__department__code=dept_code)
        section = list(sections)[0]
        section_time = list(section.section_times.all().exclude(instructor="Staff"))[0]
        difficulty_str = RPIRateMyProfessors.getProfessorDifficulty(section_time.instructor)
        return Decimal(difficulty_str)
    except:
        return None

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
            for x in courses_taken:
                if x.term == "Not Met" or len(x.term) != 6:
                    continue
                x.department_prefix = x.name.split(" ")[0]
                x.course_number = x.name.split(" ")[1]
                x.year = x.term[:-2]
                x.semester = map_month_to_semester(int(x.term[-2:]))
                fall_difficulty = getDifficulty("Fall", x.course_number, x.department_prefix)
                spring_difficulty = getDifficulty("Spring", x.course_number, x.department_prefix)
                department = Department.objects.get(code=x.department_prefix)
                new_plan_course = PlanCourse(year=x.year,semester=x.semester,
                    user=request.user.planuser,department=department,number=x.course_number, 
                    fall_difficulty=fall_difficulty, spring_difficulty=spring_difficulty)
                new_plan_course.save()
            return HttpResponseRedirect("/#/planner/");
    else:
        if request.user.planuser.first_semester:
            return HttpResponse("You have already uploaded a capp report")
        form = CappReportField()
    return render_to_response('planner/upload_capp.html', {'form': form}, context_instance=RequestContext(request))
