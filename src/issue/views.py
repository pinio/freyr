# from django.shortcuts import render
# from collections import defaultdict

from iso8601 import parse_date
from jsonview.decorators import json_view

from .models import ISSUE_TYPES, Issue

PERCENTILES = (50, 70, 80, 85, 90, 95)


def _get_default_percentile_dict():
    pd = {
        cat: {"lead_times": [], "nth_percentiles": {perc: 0 for perc in PERCENTILES}}
        for cat in set(dict(ISSUE_TYPES)) | {"expedite"}
    }
    pd["global"] = {
        "lead_times": [],
        "nth_percentiles": {perc: 0 for perc in PERCENTILES},
    }
    return pd


def _calculate_nth_percentile(items, nth):
    if not items:
        return 0
    size = len(items)
    idx = round(size * nth / 100)
    return items[idx - 1]


@json_view
def percentiles(request):
    start_date = parse_date(request.POST["start_date"])
    end_date = parse_date(request.POST["end_date"])
    pid = request.POST["project"]

    issues = list(
        Issue.objects.filter(
            project_id=pid,
            kanban_start_date__gte=start_date,
            kanban_end_date__lte=end_date,
            invalid=False,
        ).order_by("kanban_lead_time")
    )
    project = issues[0].project

    repos = {"project": _get_default_percentile_dict()}
    for issue in issues:
        repo = issue.repo.code
        # Preload empty repo data if it doesn't exist
        if repo not in repos:
            repos[repo] = _get_default_percentile_dict()

        category = "expedite" if issue.service == "expedite" else issue.type
        if not category:
            category = "feature"

        repos[repo][category]["lead_times"].append(issue.kanban_lead_time)
        repos[repo]["global"]["lead_times"].append(issue.kanban_lead_time)
        repos["project"][category]["lead_times"].append(issue.kanban_lead_time)
        repos["project"]["global"]["lead_times"].append(issue.kanban_lead_time)

    for repo in repos.values():
        for category in repo.values():
            for perc in PERCENTILES:
                percentile = _calculate_nth_percentile(category["lead_times"], perc)
                category["nth_percentiles"][perc] = percentile

    return {"project": project, **repos}
