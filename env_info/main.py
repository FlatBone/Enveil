import os
import platform
import subprocess
import sys
import json

def run_command(cmd):
    try:
        # Windowsの場合はPowerShellコマンドを適切に実行
        if os.name == 'nt' and (cmd.startswith("Get-") or cmd.startswith("wmic") or cmd.startswith("(Get-")):
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"コマンド実行エラー: {cmd} - {e}")
        return "N/A"

def format_ram_windows(raw_ram):
    # PowerShellの出力をGBに変換して整形
    try:
        # 既にGB単位で取得しているので、単純に数値部分を抽出
        ram_gb = float(raw_ram.replace("GB", "").strip())
        return f"{ram_gb:.1f}GB"
    except Exception as e:
        print(f"RAM情報解析エラー: {e}")
        return raw_ram  # エラーの場合は元のデータを返す

def format_cpu_windows(raw_cpu):
    # PowerShellからのCPU情報を整形
    try:
        lines = raw_cpu.splitlines()
        for line in lines:
            if "Name" in line and ("Intel" in line or "AMD" in line):
                return line.split(':')[-1].strip()
        # 見つからない場合はモデル名を探す
        for line in lines:
            if "Name" in line:
                return line.split(':')[-1].strip()
        return raw_cpu  # それでも見つからなければ元データを返す
    except Exception:
        return raw_cpu

def get_gpu_info():
    """GPUの情報を取得する"""
    if os.name == 'nt':  # Windows
        # PowerShellを使用してGPU情報を取得
        try:
            raw_gpu = run_command("Get-CimInstance -ClassName Win32_VideoController | Select-Object -Property Name, AdapterRAM | Format-List")
            lines = raw_gpu.splitlines()
            gpus = []
            current_gpu = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_gpu and 'Name' in current_gpu:
                        # GPUメモリをMB/GBに変換
                        if 'AdapterRAM' in current_gpu:
                            try:
                                ram_bytes = int(current_gpu['AdapterRAM'])
                                if ram_bytes > 1073741824:  # 1GB以上
                                    current_gpu['AdapterRAM'] = f"{ram_bytes/1073741824:.1f}GB"
                                else:
                                    current_gpu['AdapterRAM'] = f"{ram_bytes/1048576:.0f}MB"
                            except:
                                pass
                        
                        # 名前とメモリを連結
                        if 'AdapterRAM' in current_gpu:
                            gpus.append(f"{current_gpu['Name']} ({current_gpu['AdapterRAM']})")
                        else:
                            gpus.append(current_gpu['Name'])
                    current_gpu = {}
                elif ':' in line:
                    key, value = line.split(':', 1)
                    current_gpu[key.strip()] = value.strip()
            
            # 最後のGPUを処理
            if current_gpu and 'Name' in current_gpu:
                if 'AdapterRAM' in current_gpu:
                    try:
                        ram_bytes = int(current_gpu['AdapterRAM'])
                        if ram_bytes > 1073741824:  # 1GB以上
                            current_gpu['AdapterRAM'] = f"{ram_bytes/1073741824:.1f}GB"
                        else:
                            current_gpu['AdapterRAM'] = f"{ram_bytes/1048576:.0f}MB"
                    except:
                        pass
                
                if 'AdapterRAM' in current_gpu:
                    gpus.append(f"{current_gpu['Name']} ({current_gpu['AdapterRAM']})")
                else:
                    gpus.append(current_gpu['Name'])
            
            if gpus:
                return ", ".join(gpus)
            return "GPU情報が取得できませんでした"
        except Exception as e:
            print(f"GPU情報取得エラー: {e}")
            return "GPU情報の取得に失敗しました"
    else:  # LinuxやmacOS
        try:
            # NVIDIAのGPUがある場合
            nvidia_gpu = run_command("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
            if nvidia_gpu and "N/A" not in nvidia_gpu:
                # NVIDIAのGPU情報を整形
                gpus = []
                for line in nvidia_gpu.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 2:
                            gpu_name = parts[0].strip()
                            gpu_memory = parts[1].strip()
                            gpus.append(f"{gpu_name} ({gpu_memory})")
                if gpus:
                    return ", ".join(gpus)
            
            # AMD GPUまたはIntel GPUの確認（Linux）
            lspci_gpu = run_command("lspci | grep -i 'vga\\|3d\\|2d'")
            if lspci_gpu and "N/A" not in lspci_gpu:
                return lspci_gpu
                
            # macOSの場合
            if platform.system() == 'Darwin':
                mac_gpu = run_command("system_profiler SPDisplaysDataType | grep 'Chipset Model:'")
                if mac_gpu and "N/A" not in mac_gpu:
                    return mac_gpu.replace("Chipset Model:", "").strip()
            
            return "GPU情報が取得できませんでした"
        except Exception as e:
            print(f"GPU情報取得エラー: {e}")
            return "GPU情報の取得に失敗しました"

def get_detailed_windows_info():
    """詳細なWindowsの情報を取得する"""
    try:
        # OSの基本情報を取得
        os_info = platform.system() + " " + platform.release()
        
        # エディション情報を取得 (Home, Pro, Enterprise など)
        edition_info = run_command("(Get-CimInstance -ClassName Win32_OperatingSystem).Caption")
        if edition_info and "Microsoft" in edition_info:
            # 余分な部分を削除して整形
            edition = edition_info.replace("Microsoft ", "")
        else:
            edition = os_info
            
        # バージョン情報を取得 (22H2 など)
        version_info = run_command("(Get-CimInstance -ClassName Win32_OperatingSystem).Version")
        display_version = run_command("(Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' -Name DisplayVersion -ErrorAction SilentlyContinue).DisplayVersion")
        
        # DisplayVersionが取得できた場合（Windows 10/11）は表示する
        if display_version and display_version != "N/A":
            result = f"{edition} {display_version}"
        # バージョン番号が取得できた場合はそれを表示
        elif version_info and version_info != "N/A":
            result = f"{edition} (Version: {version_info})"
        else:
            result = edition
            
        return result
    except Exception as e:
        print(f"詳細なOS情報取得エラー: {e}")
        return platform.system() + " " + platform.release()

def get_detailed_linux_info():
    """詳細なLinuxの情報を取得する"""
    try:
        # ディストリビューション情報を取得
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                
            os_info = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # 値から引用符を削除
                    os_info[key] = value.strip('"\'')
            
            if 'PRETTY_NAME' in os_info:
                return os_info['PRETTY_NAME']
            elif 'NAME' in os_info and 'VERSION' in os_info:
                return f"{os_info['NAME']} {os_info['VERSION']}"
        
        # 上記で取得できなかった場合はlsb_releaseを試す
        lsb_info = run_command("lsb_release -ds")
        if lsb_info and lsb_info != "N/A":
            return lsb_info
            
        # それでも取得できなかった場合
        return platform.system() + " " + platform.release()
    except Exception as e:
        print(f"詳細なOS情報取得エラー: {e}")
        return platform.system() + " " + platform.release()

def get_detailed_macos_info():
    """詳細なmacOSの情報を取得する"""
    try:
        # macOSバージョン（コードネーム含む）を取得
        product_version = run_command("sw_vers -productVersion")
        product_name = run_command("sw_vers -productName")
        
        if product_name and product_version and "N/A" not in product_name:
            # コードネームを取得（Big Sur, Montereyなど）
            codename_map = {
                "10.15": "Catalina",
                "11": "Big Sur",
                "12": "Monterey",
                "13": "Ventura",
                "14": "Sonoma"
            }
            
            # バージョン番号に基づいてコードネームを決定
            major_version = product_version.split('.')[0]
            if major_version == "10":
                minor_version = product_version.split('.')[1]
                version_key = f"10.{minor_version}"
            else:
                version_key = major_version
                
            codename = codename_map.get(version_key, "")
            if codename:
                return f"{product_name} {product_version} ({codename})"
            else:
                return f"{product_name} {product_version}"
        else:
            return platform.system() + " " + platform.release()
    except Exception as e:
        print(f"詳細なOS情報取得エラー: {e}")
        return platform.system() + " " + platform.release()

def get_detailed_os_info():
    """OSの詳細情報を取得する"""
    system = platform.system()
    
    if system == "Windows":
        return get_detailed_windows_info()
    elif system == "Linux":
        return get_detailed_linux_info()
    elif system == "Darwin":  # macOS
        return get_detailed_macos_info()
    else:
        return system + " " + platform.release()

def load_software_from_config():
    """config.jsonからソフトウェアリストを読み込む"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("software", {})
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return {}
    return {}

def prompt_yes_no(question, default="y"):
    """デフォルト値付きのyes/noプロンプト"""
    valid = {"y": True, "n": False, "": True if default == "y" else False}
    prompt = f"{question} [y/n] (default '{default}'): "
    while True:
        choice = input(prompt).lower().strip()
        if choice in valid:
            return valid[choice]
        print("Please respond with 'y' or 'n' (or press Enter for default).")

def get_env_info(args=None):
    """環境情報を取得する（引数または対話形式）"""
    # コマンドライン引数の処理
    if args is not None:
        hw = "--hardware" in args
        os_info = "--os" in args
        sw = "--software" in args
        software_list = []
        for arg in args:
            if arg.startswith("--software="):
                software_list = arg.split("=")[1].split(",")
    else:
        # 対話形式での質問（デフォルトy）
        print("\n=== 情報取得の選択 / Select Information to Retrieve ===")
        print("以下の質問に'y'（はい）または'n'（いいえ）で答えてください。Enterキーでデフォルト（y）が選択されます。")
        print("Answer the following with 'y' (yes) or 'n' (no). Press Enter for default (y).")
        
        hw = prompt_yes_no("ハードウェア情報いる？/Do you need hardware information?")
        os_info = prompt_yes_no("OS情報いる？/Do you need the OS info?")
        sw = prompt_yes_no("ソフトウェアのバージョンいる？/Do you need the software version?")
        software_list = None  # 対話形式では後で設定

    result = {}
    
    if hw:
        if os.name == 'nt':  # Windows
            print("ハードウェア情報を取得中.../retrieving hardware information...")
            # PowerShellのコマンドを使用
            raw_cpu = run_command("Get-CimInstance -ClassName Win32_Processor | Format-List Name")
            # RAMの取得もPowerShellを使用
            raw_ram = run_command("(Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory/1GB")
            result["CPU"] = format_cpu_windows(raw_cpu)
            result["RAM"] = format_ram_windows(raw_ram)
            # GPU情報を追加
            result["GPU"] = get_gpu_info()
        else:  # Linuxとか
            result["CPU"] = run_command("lscpu | grep 'Model name' | cut -d: -f2-")
            result["RAM"] = run_command("free -h | grep 'Mem:' | awk '{print $2}'")
            # GPU情報を追加
            result["GPU"] = get_gpu_info()
    
    if os_info:
        # 詳細なOS情報を取得
        result["OS"] = get_detailed_os_info()
    
    if sw:
        # config.jsonからソフトウェアリストを取得
        config_software = load_software_from_config()
        
        if args and software_list:  # コマンドライン引数から指定された場合
            software_to_check = {name: cmd for name, cmd in config_software.items() if name in software_list}
            if not software_to_check:  # 指定されたものがconfigにない場合
                software_to_check = {
                    "Python": "python --version || python3 --version",
                    "Docker": "docker --version",
                    "Git": "git --version",
                    "VSCode": "code -v",
                    "Node.js": "node -v"
                }
                software_to_check = {k: v for k, v in software_to_check.items() if k.lower() in [s.lower() for s in software_list]}
        else:
            # 対話形式の場合
            print("\n=== ソフトウェアバージョンの選択 / Select Software Versions ===")
            print("チェックしたいソフトウェアを選んでください。Enterでデフォルト（y）が選択されます。")
            print("Select the software versions to check. Press Enter for default (y).")
            
            software_to_check = {}
            default_software = {
                "Python": "python --version || python3 --version",
                "Docker": "docker --version",
                "Git": "git --version",
                "VSCode": "code -v",
                "Node.js": "node -v"
            }
            
            # config.jsonのソフトウェアを優先的に確認
            for name, cmd in config_software.items():
                if prompt_yes_no(f"- {name}?"):
                    software_to_check[name] = cmd
            
            # デフォルトのソフトウェア（configにないもの）を追加で確認
            for name, cmd in default_software.items():
                if name not in software_to_check and prompt_yes_no(f"- {name}?"):
                    software_to_check[name] = cmd
        
        # ソフトウェアバージョンの取得
        for name, cmd in software_to_check.items():
            result[name] = run_command(cmd)
    
    return result

def main():
    # コマンドライン引数のチェック
    if len(sys.argv) > 1:
        env = get_env_info(sys.argv[1:])
    else:
        env = get_env_info()
    
    print("\n=== Result ===")
    for key, value in env.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()