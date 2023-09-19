# URL Protection Checker

A Django admin area to maintain a list of URLs that are publicly accessible on GOV.UK PaaS and a [scheduled job running every hour in Jenkins](https://jenkins.ci.uktrade.digital/job/url%20protection%20checker-scheduler/) which runs:

- `python manage.py load_spaces_db` get the list of available spaces from GOV.UK PaaS.
- `python manage.py daily_check` perform the check and, unless a URL is whitelisted in the URL Protection Checker, alerts if the URL is not protected by Staff SSO or the IP Filter.

URL Protection Checker is been hosted in GOV.UK PaaS Ireland so that it could run the checks from outside the IP Filter.

## Adding a new admin user

Access is controlled via Staff SSO. To grant someone access, make sure that "url protection checker" is checked for them under permitted applications.

Their user record will be created the first time they vist the admin section.

If you need to edit their user, make them a superuser etc., this can only be done after their user record has been created.

## Working on the application

### Git branching strategy

This repository uses [Git Flow](https://www.gitkraken.com/learn/git/git-flow).

However, `paketobuildpacks/builder` can't deal with slashes (`/`) in branch names, so no `feature/...` etc. please.

### Managing your shell's environment variables

A good way to manage the ones you want in your shell is to use [direnv](https://direnv.net/) with a `.envrc` file based on the `.envrc.sample` file in the root of this repository.

### Running the application locally with Docker Compose

Make yourself a `.env` based on `.env.sample`: `cp .env.sample .env`

There is a [Makefile](./Makefile) with commands to help you.

If it is the first time, or you have made changes to the application:

```shell
make build
```

Otherwise, just start the application with:

```shell
make up
```

This will run any migrations before starting the application.
