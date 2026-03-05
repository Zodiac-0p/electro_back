#!/usr/bin/env python
import os
import sys

def main():
    if not os.getenv("DJANGO_SETTINGS_MODULE"):
        settings_module = "config.deployment" if os.getenv("RENDER_EXTERNAL_HOSTNAME") else "config.settings"
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()