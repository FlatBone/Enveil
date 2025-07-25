import argparse
import json
import logging
from typing import Dict, Any

from .api import EnveilAPI
from .utils.exceptions import EnveilException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def display_results(results: Dict[str, Any]):
    """
    収集した情報を整形して表示します。
    """
    print(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    """
    コマンドライン引数を処理し、EnveilAPIを呼び出して情報を収集・表示します。
    """
    parser = argparse.ArgumentParser(
        description="A cross-platform environment information tool."
    )
    parser.add_argument(
        "--hardware",
        action="store_true",
        help="Display hardware information (CPU, RAM, GPU) only."
    )
    parser.add_argument(
        "--os",
        action="store_true",
        help="Display OS information only."
    )
    parser.add_argument(
        "--software",
        nargs='*',
        help="Display version information for specified software. If no arguments are given, all configured software will be checked."
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Specify the path to a custom configuration file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed debug logging."
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        api = EnveilAPI(config_path=args.config)
        results = {}

        # If no flags are specified, get all information
        no_flags = not (args.hardware or args.os or args.software is not None)

        if args.hardware or no_flags:
            results['hardware'] = api.get_hardware_info()

        if args.os or no_flags:
            results['os'] = api.get_os_info()

        if args.software is not None or no_flags:
            software_list = args.software if args.software is not None and args.software != [] else None
            results['software'] = api.get_software_info(software_list=software_list)

        display_results(results)

    except EnveilException as e:
        logging.error(f"An error occurred: {e}")
        print(f"[ERROR] {e}")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"[CRITICAL] An unexpected error occurred. Please check the log file for details.")

if __name__ == "__main__":
    main()
