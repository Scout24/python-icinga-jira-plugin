# Plugin for Icinga to automatically report alerts to Jira

Icinga offers the possibility to relay notifications via command scripts. This plugin is intended to forward these
notifications automatically into a Jira ticket system.

This plugin currently only handles the following notification types:

* ``PROBLEM`` for service and host problems
* ``RECOVERY`` for service and host problems

This plugin is written in Python. It works on Python 2.6 and 2.7.

For installation instructions and development issues please go into our wiki:

https://github.com/ImmobilienScout24/python-icinga-jira-plugin/wiki

## Contributors

* Oliver Hoogvliet <oliver@hoogvliet.de>
* Maximilien Riehl <maximilien.riehl@gmail.com>
* Valentin Haenel <valentin@haenel.co>
