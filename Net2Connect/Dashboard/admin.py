from django.contrib import admin
from .models import Project, Categories
from Accounts.models import Skill

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'start_date', 'end_date', 'points')
    list_display_links = ('title',)
    list_filter = ('status', 'access_type', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    ordering = ('-created_at',)

    # For easier selection of M2M fields
    filter_horizontal = ('members', 'invited_users', 'required_skills')

    readonly_fields = ('created_at', 'updated_at')

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
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

# Optional: Register Skill if not already registered
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
