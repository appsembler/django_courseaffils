from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from courseaffils.models import Course


class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course

    if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
        course_string = settings.COURSEAFFILS_COURSESTRING_MAPPER.widget()

    add_user = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Add users to group (one per line)",
        help_text=(
            "Put a [ * ] in front of the username to make "
            "them faculty.  If you add an optional <code>:"
            "&lt;password></code> after the username, the "
            "password on the account will also be set.  <br />"
            "Example: <code>*faculty1:this_is_insecure</code> "
            "creates an instructor account 'faculty1' with the "
            "password 'this_is_insecure' "),
    )

    users_to_remove = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=User.objects.none(),
        label="Remove users from group",
    )

    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            self.fields['group'].required = False
        if self.instance.user_set:
            faculty = self.instance.faculty
            ruf = self.fields['users_to_remove']
            ruf.queryset = self.instance.user_set
            ruf.choices = [
                (u.pk,
                 '%s [%s] %s' % (u.get_full_name(),
                                 u.username,
                                 '(instructor)' if u in faculty else ''
                                 )
                 )
                for u in self.instance.user_set.all()
            ]

    def clean(self):
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER')  \
                and self.cleaned_data.get('course_string', False):
            m = settings.COURSEAFFILS_COURSESTRING_MAPPER
            stud_grp, fac_grp = m.get_groups(
                self.cleaned_data['course_string'])
            if fac_grp:
                self.cleaned_data['faculty_group'] = fac_grp
            self.cleaned_data['group'] = stud_grp
        elif not self.cleaned_data['group']:
            msg = 'You must select a group'
            if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
                msg = msg + ' or enter a course string'
                if not 'course_string' not in self._errors:
                    self._errors['course_string'] = forms.util.ErrorList()
                self._errors['course_string'].append(msg)
                if 'course_string' in self.cleaned_data:
                    del self.cleaned_data["course_string"]
            self._errors['group'] = forms.util.ErrorList([msg])
            if 'group' in self.cleaned_data:
                self.cleaned_data["group"]
            raise forms.ValidationError(msg)

        if Course.objects.filter(
                group=self.cleaned_data['group']).exclude(pk=self.instance.pk):
            msg = "The group you selected is already associated with a course."
            self._errors['group'] = forms.util.ErrorList([msg])
            raise forms.ValidationError(msg)

        #run here, so the cleaned group from above can be used
        self._clean_add_user()

        return self.cleaned_data

    def clean_users_to_remove(self):
        users = self.cleaned_data['users_to_remove']
        if self.instance.group_id:
            group = self.instance.group

            for user in users:
                user.groups.remove(group)
        return users

    def _clean_add_user(self):
        """run in clean() so we can process users after course is created
        from course-string
        """
        usernames = self.cleaned_data['add_user']
        if not usernames:
            return

        #take it from here, in case instance is not yet created
        group = self.cleaned_data['group']
        for line in usernames.split('\n'):
            clean_line = line.strip().rstrip().split(':')
            username = clean_line[0]
            password = clean_line[1] if len(clean_line) > 1 else False
            also_faculty = False
            if username.startswith('*'):
                username = username[1:]
                also_faculty = True
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User(username=username)
                    if password:
                        user.set_password(password)
                    user.save()
                user.groups.add(group)
                if also_faculty and self.cleaned_data['faculty_group']:
                    user.groups.add(self.cleaned_data['faculty_group'])
        return usernames
