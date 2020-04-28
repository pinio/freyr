from djongo import models
from utils.gh import get_github_project, get_github_repo


class Repository(models.Model):
    _id = models.ObjectIdField()
    organization = models.CharField(max_length=64)
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    min_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = "Repositories"

    @property
    def identifier(self):
        return f"{self.organization}/{self.code}"

    @property
    def github(self):
        return get_github_repo(self.identifier)

    def __str__(self):
        return f"{self.name} ({self.identifier})"


class ProjectColumn(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    groups = models.CharField(max_length=250)
    valid_wip = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Project(models.Model):
    _id = models.ObjectIdField()
    github_id = models.PositiveIntegerField(null=True, blank=True)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=128)
    columns = models.ArrayField(model_container=ProjectColumn)
    repositories = models.ArrayReferenceField(to=Repository, on_delete=models.CASCADE)

    @property
    def github(self):
        return get_github_project(self.github_id)

    def __str__(self):
        return f"{self.name} ({self.number})"
