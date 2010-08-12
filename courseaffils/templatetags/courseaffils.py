from django import template
from djangohelpers.templatetags import TemplateTagNode

register = template.Library()

class GetCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        #import here, because it doesn't work above
        from courseaffils.models import Course
        return Course.objects.filter(group__in=user.groups.all())

register.tag('get_courses', GetCourses.process_tag)

class CourseRole(TemplateTagNode):
    noun_for = {"for": "user", "in": "course"}

    def __init__(self, varname, user, course):
        TemplateTagNode.__init__(self, varname, user=user, course=course)

    def execute_query(self, user, course):
        if not user in course.members:
            return "non-member"
        elif user in course.faculty:
            return "instructor"
        else:
            return "student"



register.tag('course_role', CourseRole.process_tag)
