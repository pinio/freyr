from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

from issue.models import Issue

from ...models import Project


class Command(BaseCommand):
    help = "Fetch all issues for all repos on a project"

    def add_arguments(self, parser):
        parser.add_argument("project_id", type=int)
        parser.add_argument("-r", "--repo", type=str)
        parser.add_argument("-a", "--all", type=bool)

    def handle(self, *args, **options):
        pid = options["project_id"]
        try:
            project = Project.objects.get(github_id=pid)
        except Project.DoesNotExist:
            raise CommandError(f"Project {pid} not found")

        if options.get("repo"):
            code = options["repo"]
            repos = project.repositories.filter(code=code)
            self.stdout.write(f"Fetching all issues for project {pid} on repo {code}")
        else:
            repos = project.repositories.all()
            self.stdout.write(f"Fetching all issues for project {pid}")

        created = updated = 0
        for repo in repos:
            self.stdout.write(f"- Fetching from repo {repo}")
            issues = []

            last_issue_on_db = (
                Issue.objects.filter(repo=repo).order_by("-updated_at").first()
            )
            extra = {}
            if not options.get("all", False) and last_issue_on_db:
                extra = {"since": last_issue_on_db.updated_at + timedelta(seconds=1)}
            elif repo.min_date:
                extra = {"since": repo.min_date}

            issues = list(repo.github.get_issues(state="all", **extra))

            self.stdout.write(f"-- Found {len(issues)} issues. Upserting on db")
            for issue in issues:
                if "pull_request" in issue.raw_data:
                    continue
                self.stdout.write(f"Fetching issue {issue.number} - {issue.title}")
                db_issue = Issue.objects.filter(
                    number=issue.number, repo_id=repo._id, project_id=project._id
                ).first()

                if db_issue:
                    updated += 1
                else:
                    # Not found. Create one
                    created += 1
                    db_issue = Issue(number=issue.number, repo=repo, project=project)

                db_issue.save()

        if created or updated:
            self.stdout.write(
                self.style.SUCCESS(f"Issues created: {created} / updated: {updated}")
            )
        else:
            self.stdout.write(self.style.WARNING(f"Nothing to do"))
