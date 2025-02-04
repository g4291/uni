#!/usr/bin/env python3


from ..version import VERSION


if __name__ == "__main__":
    help = f"""Available commands:

    python3 -m uni.cmd.user
        - manage users
    python3 -m uni.cmd.config
        - manage configuration

uni version: {VERSION}
"""
print(help)