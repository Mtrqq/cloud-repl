import asyncio

from crepl.api import get_endpoint_for_lang
from crepl.cli import cmdline_arguments
from crepl.execute import execute_code


def main() -> None:
    arguments = cmdline_arguments()
    endpoint = get_endpoint_for_lang(arguments.base_url, arguments.language)

    asyncio.run(execute_code(code=arguments.code, endpoint=endpoint))
