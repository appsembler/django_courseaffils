from django import forms
from django.contrib.auth.models import User
from courseaffils.models import Course

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
    
    add_user = forms.CharField(required=False)

    users_to_remove = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=User.objects.all(),
        label="Remove users from group",
        )

    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        field = self.fields['users_to_remove']
        field.queryset = field._choices = self.instance.user_set.all()
        
    def clean_users_to_remove(self):
        users = self.cleaned_data['users_to_remove']
        group = self.instance.group

        for user in users:
            user.groups.remove(group)
        return users

    def clean_add_user(self):
        username = self.cleaned_data['add_user']
        if not username:
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.save()

        user.groups.add(self.instance.group)

        return user
