from django import template

register = template.Library()

@register.filter
def status_class(student, project):
    if student in project.invited_users.all():
        return "Invited"
    elif student in project.members.all():
        return "Member"
    else:
        return "NotAssociated"
