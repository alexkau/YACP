# Decouple the logic of mapping months to semesters from the views which may need this logic implemented
def map_month_to_semester(month):
    if month == 1: # Spring
        semester_id = 0
    elif month == 5: # Summer
        semester_id = 1
    else: # Fall
        semester_id = 2 
    return semester_id

