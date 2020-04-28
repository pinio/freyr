import sys

from django.core.management.base import BaseCommand

from github import GithubException
from utils.gh import get_github_organization, get_github_repo


class Command(BaseCommand):
    help = "List projects associated with an organization"

    def add_arguments(self, parser):
        parser.add_argument(
            "org_or_repo",
            type=str,
            help="Use the org or org/repo format for fetching related projects",
        )

    def handle(self, *args, **options):
        org_or_repo = options["org_or_repo"]
        try:
            if "/" in org_or_repo:
                gh_obj = get_github_repo(org_or_repo)
            else:
                gh_obj = get_github_organization(org_or_repo)
            projects = list(gh_obj.get_projects())
            if not projects:
                self.stdout.write(
                    self.style.WARNING(f"No projects found for {org_or_repo}")
                )
                sys.exit(0)

            self.stdout.write(self.style.SUCCESS("Found github projects data"))
            for project in projects:
                self.stdout.write(f"{project.id} -- {project.name}")
        except GithubException as err:
            self.stdout.write(
                self.style.ERROR(f"Error fetching data from github - {err}")
            )
