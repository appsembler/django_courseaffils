from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from courseaffils.models import Course, CourseAccess
from django.db.models import get_model, Q
from django.utils.http import urlquote
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
import datetime
import simplejson


def available_courses_query(user):
    available_courses = None
    if user.is_staff:
        available_courses = Course.objects.all()
    else:
        available_courses = Course.objects.filter(group__user=user)

    return available_courses.order_by('-info__year', '-info__term', 'title')


def select_course(request):
    available_courses = available_courses_query(request.user)

    list_all_link = True
    if not request.GET.has_key('list_all'):
        current_year = datetime.datetime.now().year
        available_courses = available_courses.exclude(
            info__year__lt=current_year)
        list_all_link = False

    response_dict = {'request': request,
                     'user': request.user,
                     'add_privilege': request.user.is_staff,
                     'courses': available_courses,
                     'list_all_link': list_all_link,
                     }

    if len(available_courses) == 0 and not request.user.is_staff:
        return render_to_response('courseaffils/no_courses.html',
                                  response_dict)

    response_dict['next_redirect'] = ''
    if request.META.has_key('QUERY_STRING') \
            and not request.GET.has_key('unset_course'):
            #just GET (until someone complains)
        response_dict['next_redirect'] = '&next=%s' % (
            urlquote(request.get_full_path()))

    return render_to_response('courseaffils/select_course.html',
                              response_dict)

SESSION_KEY = 'ccnmtl.courseaffils.course'


def is_logged_in(request):
    """This could be a privacy hole, but since it's just logged in status,
     it seems pretty harmless"""
    logged_in = request.user.is_authenticated()
    course_selected = request.session.has_key(SESSION_KEY)
    data = {
        "logged_in": logged_in,
        "course_selected": course_selected,  # just truth value
        "ready": (logged_in and course_selected),
    }
    jscript = """(function() {
                   var status = %s;
                   if (window.SherdBookmarklet) {
                       window.SherdBookmarklet.update_user_status(status);
                   }
                   if (!window.SherdBookmarkletOptions) {
                          window.SherdBookmarkletOptions={};
                   }
                   window.SherdBookmarkletOptions.user_status = status;
                  })();
              """ % simplejson.dumps(data)
    return HttpResponse(jscript,
                        mimetype='application/javascript')


def course_list_query(request):
    if not CourseAccess.allowed(request):
        return HttpResponseForbidden('{"error":"server not whitelisted"}')
    user = get_object_or_404(
        User, username=request.REQUEST.get('user', 'none'))
    courses = available_courses_query(user)
    data = {'courses': dict(
            [(c.group.name, {'title': c.title, })
             for c in courses]
            )}
    return HttpResponse(
        simplejson.dumps(data, indent=2),
        mimetype='application/json')


def refresh_and_close_window(request):
    pass
