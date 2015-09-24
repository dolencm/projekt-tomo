from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    class Meta:
        ordering = ['last_name', 'first_name']

    def is_teacher(self, course):
        return course.teachers.filter(pk=self.id).exists()

    def is_student(self, course):
        return course.students.filter(pk=self.id).exists()

    def can_edit_course(self, course):
        return self.is_teacher(course)

    def can_edit_problem_set(self, problem_set):
        return self.can_edit_course(problem_set.course)

    def can_edit_problem(self, problem):
        return self.can_edit_problem_set(problem.problem_set)

    def can_view_course_attempts(self, course):
        return self.is_teacher(course)

    def can_view_problem_set_attempts(self, problem_set):
        return self.can_view_course_attempts(problem_set.course)

    def is_favourite_course(self, course):
        return self.is_teacher(course) or self.is_student(course)

    def can_view_course(self, course):
        return True

    def can_view_problem_set(self, problem_set):
        return self.can_view_course(problem_set.course) and \
               (problem_set.visible or self.is_teacher(problem_set.course))

    def can_view_problem(self, problem):
        return self.can_view_problem_set(problem.problem_set)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
