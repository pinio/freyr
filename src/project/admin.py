from django.contrib import admin
from django.utils.html import format_html

from .models import Project, Repository


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "code", "github_url")

    def github_url(self, obj):
        return format_html(
            "<a href='https://github.com/{path}' target=_blank>{path}</a>",
            path=f"{obj.organization}/{obj.code}",
        )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "github_id", "column_codes")

    def column_codes(self, obj):
        return " > ".join([c.code for c in obj.columns])
