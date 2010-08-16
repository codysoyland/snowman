from django.contrib import admin
from repocracy.repo.models import Repository

class RepositoryAdmin(admin.ModelAdmin):
    actions = ['update_from_origin']

    def update_from_origin(self, request, queryset):
        for obj in queryset:
            obj.update()

    update_from_origin.short_description = 'Update repository from origin'

admin.site.register(Repository, RepositoryAdmin)
