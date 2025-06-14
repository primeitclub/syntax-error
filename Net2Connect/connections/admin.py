from django.contrib import admin
from .models import ConnectionRequest
@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'accepted')
    list_filter = ('accepted', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_user', 'to_user')
# Register your models here.
