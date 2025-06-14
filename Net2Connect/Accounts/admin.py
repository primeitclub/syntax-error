from django.contrib import admin
from .models import Student, Skill,Project

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'points', 'date_joined')
    search_fields = ('user_name', 'email')
    list_filter = ('date_joined', 'points')
    
    # These fields will be displayed but **cannot** be edited
    readonly_fields = ('user', 'user_name', 'date_joined', 'last_active')

    fieldsets = (
        (None, {
            'fields': ('user', 'user_name', 'email', 'points', 'description', 'interest_fields', 'number_of_connections', 'github_url', 'facebook_url', 'linkedin_url')
        }),
        ('Skills', {
            'fields': ('skills',)
        }),
        ('Activity', {
            'fields': ('date_joined', 'last_active')
        }),
    )


admin.site.register(Student, StudentAdmin)

# Register other models normally
admin.site.register(Skill)
admin.site.register(Project)
