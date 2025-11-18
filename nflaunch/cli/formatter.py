"""Custom argument parser formatters for the nflaunch CLI."""

import argparse


class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
    ) -> None:
        super().__init__(
            prog,
            indent_increment=indent_increment,
            max_help_position=max_help_position,
            width=width,
        )
        self._max_help_position = 35  # adjust after base init

    def _get_help_string(self, action: argparse.Action) -> str:
        help_text = action.help or ""
        if action.required:
            help_text += " (required)"
        else:
            help_text += " (optional)"
        if action.default not in (argparse.SUPPRESS, None, False, {}):
            help_text += f" (default: '{action.default}')"
        return help_text
