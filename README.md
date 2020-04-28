# Freyr - Kanban Metrics for Github Board

This project aims to fetch and work with metrics from a common Github board.

## Disclaimer

This project is in early alpha stage. It shouldn't in theory break anything, but don't blame me if it sets your computer on fire, or sends troll messages to your relatives.

## Name origin

Freyr (Old Norse: “[the] Lord”) is the god of prosperity (source: Wikipedia).

## Requirements

- MongoDB 4.0 or above
- Python 3.6 or above

## Quickstart

1. Set up a local MongoDB server instance
1. Create a Github token with access to the project(s) you want to collect data from
1. Set the environment variable GITHUB_PROJECTS_ACCESS_TOKEN
1. Create a virtualenv and install everything from requirements.txt
1. Create a superuser on Django Admin (`python src/manage.py createsuperuser`)
1. Run `src/manage.py list_projects`. The first column shows your projects IDs
1. Run `src/manage.py runserver`
1. Access 127.0.0.1:8000/admin
1. Add at least one Repository (by organization and repo) and one Project (using the ID above)
1. Run `src/manage.py sync_project :project_id`. Optionally you can also inform the `-r repo` param to limit fetching data from a single repository.
1. If the command above is taking too long, you can set a minimum date on the repo configuration to fech only data starting from that date
1. For now, you can use curl to see the output json for percentiles. Just use:
```
curl --location --request POST 'localhost:8000/issue/percentiles/' \
    --form 'start_date=2020-01-01' \
    --form 'end_date=2020-06-01' \
    --form 'project=:object_id_for_project_on_admin'
```
(The project object ID can be seen on the URL when you open the project on the admin page)

## Detailed instructions

### Installing MongoDB

For now, _freyr_ only supports a local mongodb server instance. You can customize settings.py if you want.
Installation instructions: https://docs.mongodb.com/manual/installation/

### Github personal access token

https://help.github.com/en/enterprise/2.17/user/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

### Creating a virtualenv and installing requirements.txt

I suggest using virtualenvwrapper -- https://virtualenvwrapper.readthedocs.io/en/latest/
Then using:
```sh
mkvirtualenv freyr
pip install -r requirements.txt
```

## Supported Python/MongoDB versions

This project was tested on Python 3.6, 3.7 and 3.8, and on MongoDB 4.0 and 4.2.

## Contributing

Just make sure you use the pre-commit hooks and follow the PEP8 specification

## Versioning

_NOTE: This project is still **beta** -- versioning will start at 1.0 when ready_

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/pinio/freyr/tags).

## Authors

* **Danilo Martins** - *Initial work* - [Mawkee](https://github.com/mawkee)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
