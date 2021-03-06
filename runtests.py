from django.conf import settings
from django.core.management import call_command
from courseaffils.columbia import CourseStringMapper

def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'courseaffils',
            'django_nose',
        ),
        TEST_RUNNER = 'django_nose.NoseTestSuiteRunner',

        NOSE_ARGS = [
            '--with-coverage',
            '--cover-package=courseaffils',
            ],

        COURSEAFFILS_EXEMPT_PATHS = (
            '/accounts/',
            '/static/',
            '/site_media/',
            '/docs/',
            '/admin/',
            '/registration/',
            '/favicon.ico',
            '/smoketest/',
            ),
        COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper,
        ROOT_URLCONF = [],

        # Django replaces this, but it still wants it. *shrugs*
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'HOST': '',
                'PORT': '',
                'USER': '',
                'PASSWORD': '',
                }
            }
    )

    # Fire off the tests
    call_command('test', 'courseaffils')

if __name__ == '__main__':
    main()
