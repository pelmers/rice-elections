### How do I get started?

- Since owlection runs on Google App Engine, you'll need a copy of the [SDK for Python](https://developers.google.com/appengine/downloads).
- Once you've got that, go ahead and fork/clone this repository.
- Make sure that the src/ directory of this repository is in the GAE folder (make a symlink).
- Run the test server with `python dev_appserver.py owlection`
- Visit `localhost:8080` in your browser to see the development site.

### How do I test the admin features?

- You'll have to make yourself an admin: see the provided setup script in scripts/setup.py and add yourself to an organization and the admin list.
- With the development server running, visit `http://localhost:8000/console` in your browser.
- Execute the setup script with:

  `from scripts import setup; setup.main()`
