# Plugin for Icinga to automatically report alerts to Jira

Icinga offers the possibility to relay notifications via command scripts. This plugin is intended to forward these
notifications automatically into a Jira ticket system.

This plugin currently only handles the following notification types:

* ``PROBLEM`` for service and host problems
* ``RECOVERY`` for service and host problems

For more information, see section "Notifications and Jira" below.

This plugin is written in Python. It works on Python 2.6 and 2.7.

## Installation Guide

Installation is bound to the Icinga configuration. You will need to define a command that executes
the given plugin and a contact that uses this command.

### a) command example

    define command {
       command_name python-icinga-to-jira
       command_line /usr/bin/python /usr/lib64/icinga/plugins/icinga2jira.py --config /etc/icinga/example_config.ini
    }

There is a config example file ``example_config.ini`` in this project, that you can adapt to your needs.

### b) contact example

    define contact {
            contact_name                    jira-ticket
            alias                           jira-ticket
            service_notification_period     24x7
            host_notification_period        24x7
            service_notification_options    w,c,r,f
            host_notification_options       d,u,r,f
            service_notification_commands   python-icinga-to-jira
            host_notification_commands      python-icinga-to-jira
    }

The ``*_notification_options`` influence the way in which the plugin is
executed, for a detailed explanation, see [3].

## Notifications and Jira

Icinga supports both HOST-associated and SERVICE-associated checks. This plugin
can handle both, but outputs slightly different messages depending on the check
type.

Icinga has several different notification types ([1]), of which this plugin only
supports the following ones:

* PROBLEM - open a new Jira issue in given Jira project with a subset of given information
* RECOVERY - closes Jira issues and sets a comment with a subset of given recovery information
* ACKNOWLEDGEMENT - no action
* FLAPPINGSTART - no action
* FLAPPINGSTOP - no action
* FLAPPINGDISABLED - no action
* DOWNTIMESTART - no action
* DOWNTIMESTOP - no action
* DOWNTIMECANCELLED - no action

## Development Guide

This project uses pybuilder on a virtual environment.

Please ensure you have installed:
* python
* pip
*

With pip installed you need to install more packages:

        pip install jira-python
        pip install mock
        pip install coverage
        pip install pylint


## References

* [1] Notification Types: http://docs.icinga.org/latest/en/notifications.html#typemacro
* [2] Reference of notification variables aka Icinga macros: http://docs.icinga.org/latest/en/macrolist.html
* [3] Containing notification options: http://docs.icinga.org/latest/en/objectdefinitions.html
