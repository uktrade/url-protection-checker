# URL Protection Checker

Maintains a list of URLs that are publicly accessible on GOV.UK PaaS and, unless the URL is whitelisted in the URL Protection Checker, alerts if the URL is not protected by Staff SSO or the IP Filter.

## Adding a new admin user

Access is controlled via Staff SSO. To grant someone access, make sure that "url protection checker" is checked for them under permitted applications.

Their user record will be created the first time they vist the admin section.

If you need to edit their user, make them a super user etc., this can only be done after their user record has been created.

## Working on the application

### Managing environment variables

A good way to manage this is to use [direnv](https://direnv.net/) with a `.envrc` file based on the `.envrc.sample` file in the root of this repository.
