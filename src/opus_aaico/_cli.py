"""CLI entry point for opus-aaico."""

from opus_aaico._constants import SDK_VERSION

LOGO = r"""
   ____  ____  __  ______    ___    _    __________
  / __ \/ __ \/ / / / ___/  /   |  / \  /  _/ ____/___
 / / / / /_/ / / / /\__ \  / /| | / _ \ / // /   / __ \
/ /_/ / ____/ /_/ /___/ / / ___ |/ ___ _/ // /___/ /_/ /
\____/_/    \____//____/ /_/  |_/_/  |_/___/\____/\____/
"""


def main() -> None:
    print(LOGO)
    print(f"  opus-aaico v{SDK_VERSION}")
    print("  Built by Mo for the mission of AI")
    print()
    print("  Python SDK for the OPUS workflow automation platform")
    print()
    print("  Quick start:")
    print("    from opus_aaico import OpusClient")
    print('    client = OpusClient(api_key="sk-...")')
    print('    result = client.workflows.run("wf-123", payload={...})')
    print()
    print("  Docs:   https://github.com/moibrahim-applied/opus-aaico-python")
    print("  PyPI:   https://pypi.org/project/opus-aaico/")
    print()


if __name__ == "__main__":
    main()
