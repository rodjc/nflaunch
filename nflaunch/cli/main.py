from nflaunch.cli.parser import parse_args
from nflaunch.launcher.nextflow import NextflowLauncher


def main() -> None:
    """
    Entry point for the nflaunch CLI.
    """
    args = parse_args()

    launcher = NextflowLauncher(args)
    launcher.run()


if __name__ == "__main__":
    main()
