from piston.resource import Resource
from yacs.api import handlers

dept_handler = Resource(handlers.DepartmentHandler)
semester_handler = Resource(handlers.SemesterHandler)
bulk_course_handler = Resource(handlers.BulkCourseHandler)
course_handler = Resource(handlers.CourseHandler)
section_handler = Resource(handlers.SectionHandler)
schedule_handler = Resource(handlers.ScheduleHandler)
period_handler = Resource(handlers.PeriodHandler)

compute_schedule_handler = Resource(handlers.OldScheduleHandler)
