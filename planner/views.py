from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import PlanUser
from models import PlanCourse
from fields import CappReportField
from utils import map_month_to_semester

from courses.models import Course
from courses.models import Department
from courses.models import Section

from decimal import *

from RPICappReport import *
from RPIRateMyProfessors import *

from threading import Thread
from time import sleep
# returns the difficulty rating from RateMyProfessors for the instructor of the given course
def getDifficulty(season, course_number, dept_code):
    try:
        sections = Section.objects.filter(semester__name__startswith=season,
          course__number=course_number, course__department__code=dept_code)
        section = list(sections)[0]
        section_time = list(section.section_times.all().exclude(instructor="Staff"))[0]
        difficulty_str = RPIRateMyProfessors.getProfessorDifficulty(section_time.instructor)
        return Decimal(difficulty_str)
    except:
        return None

# view that adds the given course to the database (from CAPP report)
def addCourseTaken(request, x):
    if x.term == "Not Met" or len(x.term) != 6:
         return
    x.department_prefix = x.name.split(" ")[0]
    x.course_number = x.name.split(" ")[1]
    x.year = x.term[:-2]
    x.semester = map_month_to_semester(int(x.term[-2:]))
    credits = Course.objects.filter(number=x.course_number, department__code=x.department_prefix)[:1].get().min_credits
    department = Department.objects.get(code=x.department_prefix)
    new_plan_course = PlanCourse(
        year=x.year, semester=x.semester,
        user=request.user.planuser, department=department,
        number=x.course_number, movable=False,
        credits=credits
    )
    new_plan_course.save()
    fall_difficulty = getDifficulty("Fall", x.course_number, x.department_prefix)
    spring_difficulty = getDifficulty("Spring", x.course_number, x.department_prefix)
    new_plan_course.fall_difficulty = fall_difficulty
    new_plan_course.spring_difficulty = spring_difficulty
    new_plan_course.save()
# view that takes in a CAPP report and adds each course in the report to the database
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
            plan_user.has_uploaded_capp = True
            plan_user.save()

            # Delete all previous records, if any exist
            PlanCourse.objects.filter(user=plan_user).delete()

            threads = []

            for x in courses_taken:
                thread = Thread(target = addCourseTaken, args = (request, x, ))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            return HttpResponseRedirect("/#/planner/")
    else:
        # if request.user.planuser.first_semester:
        #     return HttpResponse("You have already uploaded a capp report")
        form = CappReportField()
    return render_to_response('planner/upload_capp.html', {'form': form}, 
                                context_instance=RequestContext(request))
# view that moves a course from one semester in the planner into a different one
@csrf_exempt
def moveCourse(request):
    # find the relevant course
    course_prefix = request.POST["course"].split(" ")[0]
    course_number = int(request.POST["course"].split(" ")[1])
    department = Department.objects.get(code=course_prefix)
    plan_course = request.user.planuser.planner_courses.get(number=course_number,department=department)
    # add the course to the database
    semester = request.POST["semester"]
    year = request.POST["year"]
    plan_course.year = year
    plan_course.semester = semester
    plan_course.save()
    return HttpResponse("success")
# view that adds a course to the planner (not from CAPP report)
@csrf_exempt
def addCourse(request):
    if "year" in request.POST:
        year = request.POST["year"]
    else:
        year = -1
    if "semester" in request.POST:
        semester = request.POST["semester"]
    else:
        semester = -1
    # find the relevant course
    course_prefix = request.POST["course"].split(" ")[0]
    course_number = int(request.POST["course"].split(" ")[1])
    department = Department.objects.get(code=course_prefix)
    exists = PlanCourse.objects.filter(user=request.user.planuser,
        number=course_number,department=department).count() > 0
    if exists:
        return HttpResponse("already in planner")
    credits = Course.objects.filter(number=course_number, department=department)[:1].get().min_credits
    plan_course = PlanCourse(user=request.user.planuser,number=course_number,department=department,
        year=year,semester=semester,credits=credits)
    # add course to db before making request to RateMyProfessor
    plan_course.save()
    # find out course difficulty and save to db
    fall_difficulty = getDifficulty("Fall", course_number, course_prefix)
    spring_difficulty = getDifficulty("Spring", course_number, course_prefix)
    plan_course.fall_difficulty=fall_difficulty
    plan_course.spring_difficulty=spring_difficulty
    plan_course.save()

    return HttpResponse("success")
# returns whether a given course exists in the database already
@csrf_exempt
def courseExists(request):
    course_prefix = request.POST["course"].split(" ")[0]
    course_number = int(request.POST["course"].split(" ")[1])
    department = Department.objects.get(code=course_prefix)
    return HttpResponse(PlanCourse.objects.filter(user=request.user.planuser,
        number=course_number,department=department).count() > 0)
# removes a course from the database
@csrf_exempt
def removeCourse(request):
    course_prefix = request.POST["course"].split(" ")[0]
    course_number = int(request.POST["course"].split(" ")[1])
    semester = request.POST["semester"]
    year = request.POST["year"]
    department = Department.objects.get(code=course_prefix)
    plan_course = request.user.planuser.planner_courses.get(number=course_number,department=department)
    plan_course.delete()
    return HttpResponse("success")