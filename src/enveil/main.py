import argparse
import json
from typing import Dict, Any

from .api import EnveilAPI

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
        description="クロスプラットフォームで動作する環境情報取得ツール Enveil。"
    )
    parser.add_argument(
        "--hardware",
        action="store_true",
        help="ハードウェア情報（CPU, RAM, GPU）のみを表示します。"
    )
    parser.add_argument(
        "--os",
        action="store_true",
        help="OS情報のみを表示します。"
    )
    parser.add_argument(
        "--software",
        nargs='*',
        help="指定されたソフトウェアのバージョン情報を表示します。引数なしの場合は設定されているすべてのソフトウェアが対象です。"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="カスタム設定ファイルのパスを指定します。"
    )

    args = parser.parse_args()

    api = EnveilAPI(config_path=args.config)
    results = {}

    # フラグが何も指定されていない場合はすべての情報を取得
    no_flags = not (args.hardware or args.os or args.software is not None)

    if args.hardware or no_flags:
        results['hardware'] = api.get_hardware_info()

    if args.os or no_flags:
        results['os'] = api.get_os_info()

    if args.software is not None or no_flags:
        # --softwareが引数なしで指定された場合（[]）と、フラグ自体がない場合（no_flags）を区別
        # どちらも「すべて」と解釈し、APIにはNoneを渡す
        software_list = args.software if args.software is not None and args.software != [] else None
        results['software'] = api.get_software_info(software_list=software_list)

    display_results(results)

if __name__ == "__main__":
    main()
