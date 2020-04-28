from django.contrib import admin

from djongo.admin import ModelAdmin

from .models import Issue


@admin.register(Issue)
class IssueAdmin(ModelAdmin):
    readonly_fields = (
        "kanban_metrics",
        "type",
        "title",
        "type",
        "labels",
        "service",
        "timeline",
        "done",
        "created_at",
        "updated_at",
        "kanban_start_date",
        "kanban_end_date",
        "kanban_lead_time",
        "kanban_total_hold_time",
        "kanban_total_blocked_time",
        "kanban_metrics",
        "github_url",
        "invalid",
    )
    list_display = (
        "__str__",
        "type",
        "github_url",
        "kanban_lead_time",
    )
    fieldsets = (
        (
            "Identification",
            {"fields": ("title", "repo", "project", "number", "type", "github_url")},
        ),
        (
            "Metadata",
            {"fields": ("labels", "created_at", "updated_at", "invalid", "done")},
        ),
        ("Timeline", {"fields": ("timeline",)}),
        (
            "Kanban",
            {
                "fields": (
                    "kanban_start_date",
                    "kanban_end_date",
                    "kanban_lead_time",
                    "kanban_total_hold_time",
                    "kanban_total_blocked_time",
                )
            },
        ),
    )
    list_filter = ["project", "repo", "kanban_lead_time", "done"]
    list_prefetch_related = ["repo", "project"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("project", "number", "repo")
        return self.readonly_fields
