from django.utils.functional import cached_property
from django.utils.html import format_html

from djongo import models
from utils.func import as_utc
from utils.gh import get_github_issue, get_github_issue_timeline

CLASSES_OF_SERVICE = (
    ("expedite", "Expedite"),
    ("fixed", "Fixed Delivery Date"),
    ("standard", "Standard"),
    ("intangible", "Intangible"),
)
ISSUE_TYPES = (
    ("feature", "Feature"),
    ("bug", "Bug"),
    ("chore", "Chore/Maintenance"),
    ("qa", "QA Automation"),
)
EVENT_TYPES = (
    ("moved", "Card Moved On Project"),
    ("on_hold", "Card on Hold"),
    ("on_hold_removed", "Card Resumed"),
    ("blocked", "Card Blocked"),
    ("blocked_removed", "Card Unblocked"),
)
EVENT_LABEL_MAPPING = {
    "labeled": {"hold": "on_hold", "blocked": "blocked"},
    "unlabeled": {"hold": "on_hold_removed", "blocked": "blocked_removed"},
}
ISSUE_TYPE_LABEL_MAPPING = {
    "feature": "feature",
    "enhancement": "feature",
    "improvement": "feature",
    "bug": "bug",
    "chore": "chore",
    "qa": "qa",
}
TIMELINE_CARD_EVENT_TYPES = [
    "added_to_project",
    "converted_note_to_issue",
    "moved_columns_in_project",
    # "removed_from_project",
]
INVALID_ISSUE_LABELS = (
    "invalid",
    "duplicate",
    "cannot-reproduce",
    "wontfix",
    "no-report",
)


class Event(models.Model):
    type = models.CharField(max_length=16, choices=EVENT_TYPES)
    column = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()

    class Meta:
        abstract = True

    def __str__(self):
        if self.type == "moved":
            return f"{self.type} - {self.column} @ {self.date}"
        return f"{self.type} @ {self.date}"


class Issue(models.Model):
    _id = models.ObjectIdField()
    number = models.PositiveIntegerField(null=False)
    repo = models.ForeignKey("project.Repository", on_delete=models.CASCADE)
    project = models.ForeignKey("project.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=16, choices=ISSUE_TYPES, blank=True)
    labels = models.CharField(max_length=255, blank=True)
    invalid = models.BooleanField(default=False)
    # author = models.CharField(max_length=64, blank=True)
    service = models.CharField(max_length=16, choices=CLASSES_OF_SERVICE, blank=True)
    timeline = models.ArrayField(model_container=Event, blank=True)
    done = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(blank=True)
    updated_at = models.DateTimeField(blank=True)
    # Kanban stuff
    kanban_start_date = models.DateTimeField(blank=True)
    kanban_end_date = models.DateTimeField(blank=True)
    kanban_lead_time = models.PositiveIntegerField(blank=True)
    kanban_total_hold_time = models.PositiveIntegerField(blank=True)
    kanban_total_blocked_time = models.PositiveIntegerField(blank=True)
    kanban_metrics = models.DictField(default=dict)

    objects = models.DjongoManager()

    class Meta:
        # We can have the same issue on different projects
        unique_together = (("repo", "number", "project"),)

    @cached_property
    def github(self):
        return get_github_issue(self.repo.identifier, self.number)

    @property
    def github_url(self):
        return format_html(
            "<a href='https://github.com/{path}' target=_blank>{path}</a>",
            path=f"{self.repo.organization}/{self.repo.code}/issues/{self.number}",
        )

    @property
    def github_labels(self):
        return [l.name.lower() for l in self.github.labels]

    @cached_property
    def github_timeline(self):
        events = []
        project_id = self.project.github_id
        for event in get_github_issue_timeline(self.github):
            project_card = event.raw_data.get("project_card", {})
            label = event.raw_data.get("label", {})

            if event.event in EVENT_LABEL_MAPPING and label.get("name") in (
                "hold",
                "blocked",
            ):
                events.append(
                    Event(
                        type=EVENT_LABEL_MAPPING[event.event][label["name"]],
                        date=as_utc(event.created_at),
                    )
                )
            elif project_card and project_card["project_id"] == project_id:
                # Exclude "remove from project" for now
                if event.event not in TIMELINE_CARD_EVENT_TYPES:
                    continue
                events.append(
                    Event(
                        type="moved",
                        column=project_card["column_name"],
                        date=as_utc(event.created_at),
                    )
                )
        return events

    def get_service_type(self):
        if "critical" in self.github_labels:
            return "expedite"
        return "standard"

    def __str__(self):
        return f"{self.repo.code}/{self.number} - {self.title}"

    def _col(self, name):
        for column in self.project.columns:
            if column.code == name:
                return column
        # This might break something, but oh well
        return None

    @cached_property
    def _last_col_for_project(self):
        for column in self.project.columns[::-1]:
            if column.valid_wip:
                return column
        return None

    def process_timeline_data(self):
        # data = {column.code: {} for column in self.project.columns}
        # data["blocked"] = 0
        # data["on_hold"] = 0
        blocked_since = None
        on_hold_since = None
        start_date = None
        end_date = None
        lead_time = None
        blocked = 0
        on_hold = 0
        # current_column = None
        for event in self.github_timeline:
            if event.type == "on_hold":
                on_hold_since = event.date
            elif event.type == "blocked":
                blocked_since = event.date
            elif on_hold_since and event.type == "on_hold_removed":
                # Ignore on hold for less than 2 hours
                on_hold_time = on_hold_since - event.date
                on_hold_since = None
                if on_hold_time.seconds > 7200:
                    on_hold += max(on_hold_time.days, 1)
            elif blocked_since and event.type == "blocked_removed":
                # Ignore block if less than 2 hours
                blocked_time = blocked_since - event.date
                blocked_since = None
                if blocked_time.seconds > 7200:
                    blocked += max(blocked_time.days, 1)
            elif event.type == "moved":
                column = self._col(event.column)
                if start_date is None and column.valid_wip:
                    start_date = event.date
                if column.code == self._last_col_for_project.code:
                    end_date = event.date
                    lead_time = max((end_date - start_date).days, 1)
                # TODO: Handle time in each column

        return {
            "kanban_start_date": start_date,
            "kanban_end_date": end_date,
            "kanban_lead_time": lead_time,
            "on_hold": on_hold,
            "blocked": blocked,
        }

    def save(self, *args, **kwargs):
        self.title = self.github.title
        self.labels = " | ".join(self.github_labels)
        # Find the first valid issue type
        for label in self.github_labels:
            if label in ISSUE_TYPE_LABEL_MAPPING:
                self.type = ISSUE_TYPE_LABEL_MAPPING[label]
                break
        else:
            self.type = "feature"
        self.service = self.get_service_type()
        self.created_at = as_utc(self.github.created_at)
        self.updated_at = as_utc(self.github.updated_at)
        self.timeline = self.github_timeline
        self.invalid = bool(set(self.github_labels) & set(INVALID_ISSUE_LABELS))
        data = self.process_timeline_data()
        self.done = data["kanban_lead_time"] is not None
        self.kanban_start_date = data["kanban_start_date"]
        self.kanban_end_date = data["kanban_end_date"]
        self.kanban_lead_time = data["kanban_lead_time"]
        self.kanban_total_hold_time = data["on_hold"]
        self.kanban_total_blocked_time = data["blocked"]
        super().save(*args, **kwargs)
