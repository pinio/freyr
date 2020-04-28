from functools import lru_cache

from django.conf import settings

from github import Consts, Github
from github.PaginatedList import PaginatedList
from github.TimelineEvent import TimelineEvent

gh = Github(settings.GITHUB_TOKEN)


@lru_cache(maxsize=64)
def get_github_organization(organization_name):
    return gh.get_organization(organization_name)


@lru_cache(maxsize=64)
def get_github_repo(repo_name):
    return gh.get_repo(repo_name)


@lru_cache(maxsize=64)
def get_github_project(project):
    return gh.get_project(project)


@lru_cache(maxsize=2048)
def get_github_issue(repo, issue):
    gh_repo = get_github_repo(repo)
    return gh_repo.get_issue(issue)


def get_github_issue_timeline(issue):
    # This has to be a custom since PyGithub doesn't support the starfox preview
    starfox_header = "application/vnd.github.starfox-preview+json"
    headers_accept = f"{starfox_header}, {Consts.issueTimelineEventsPreview}"
    return list(
        PaginatedList(
            TimelineEvent,
            issue._requester,
            issue.url + "/timeline",
            None,
            headers={"Accept": headers_accept},
        )
    )
