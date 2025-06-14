from django.contrib import admin
from .models import Project, Category

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'start_date', 'end_date', 'points')
    list_filter = ('status', 'access_type', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    
    # For easier selection of M2M fields
    filter_horizontal = ('members', 'invited_users', 'required_skills')

    # Optional: Grouping fields in the admin form
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'owner', 'status', 'access_type', 'max_members', 'points')
        }),
        ('Date Info', {
            'fields': ('start_date', 'end_date')
        }),
        ('Collaboration', {
            'fields': ('members', 'invited_users')
        }),
        ('Matching Criteria', {
            'fields': ('required_skills', 'required_fields')
        }),
    )

admin.site.register(Project, ProjectAdmin)
admin.site.register(Category)
