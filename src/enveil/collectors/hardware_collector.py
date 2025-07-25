from typing import Any, Dict, List

from ..core.platform_detector import PlatformDetector
from .base_collector import BaseCollector

class HardwareCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        """ハードウェア情報を収集する"""
        info = {"CPU": "N/A", "RAM": "N/A", "GPU": "N/A"}

        if PlatformDetector.is_windows():
            try:
                cpu_raw = self.executor.execute("get_cpu_windows")
                info["CPU"] = self._format_cpu_windows(cpu_raw)
            except Exception:
                info["CPU"] = "N/A"

            try:
                ram_raw = self.executor.execute("get_ram_windows")
                info["RAM"] = self._format_ram_windows(ram_raw)
            except Exception:
                info["RAM"] = "N/A"

            try:
                gpu_raw = self.executor.execute("get_gpu_windows")
                info["GPU"] = self._format_gpu_windows(gpu_raw)
            except Exception:
                info["GPU"] = "N/A"
        else:
            # Linux/macOSのロジック
            try:
                info["CPU"] = self.executor.execute("get_cpu_linux").strip()
                info["RAM"] = self.executor.execute("get_ram_linux")
                info["GPU"] = self.executor.execute("get_gpu_linux")
            except Exception:
                pass
        return info

    def _format_cpu_windows(self, raw_cpu: str) -> str:
        """wmicからのCPU情報を整形"""
        try:
            for line in raw_cpu.splitlines():
                line = line.strip()
                if line.startswith("Name="):
                    return line.split("=", 1)[1].strip()
            return "N/A"
        except Exception:
            return "N/A"

    def _format_ram_windows(self, raw_ram: str) -> str:
        """wmicの出力を合計し、GBに変換して整形"""
        try:
            # ヘッダー行(Capacity)と空行を除外
            capacities = [int(line.strip()) for line in raw_ram.splitlines() if line.strip().isdigit()]
            total_capacity_bytes = sum(capacities)
            if total_capacity_bytes == 0:
                return "N/A"
            total_capacity_gb = total_capacity_bytes / (1024**3)
            return f"{total_capacity_gb:.1f}GB"
        except (ValueError, TypeError):
            return "N/A"

    def _format_gpu_windows(self, raw_gpu: str) -> str:
        """wmicからのGPU情報を整形"""
        try:
            gpus: List[str] = []
            lines = raw_gpu.strip().splitlines()
            if len(lines) < 2:
                return "N/A"

            # CSVヘッダーを探してインデックスを取得
            headers = [h.strip() for h in lines[0].split(',')]
            try:
                name_index = headers.index("Name")
                ram_index = headers.index("AdapterRAM")
            except ValueError:
                return "N/A" # 必要なヘッダーがない

            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = line.split(',')
                name = parts[name_index].strip()
                try:
                    ram_bytes = int(parts[ram_index].strip())
                    ram_gb = ram_bytes / (1024**3)
                    gpus.append(f"{name} ({ram_gb:.1f}GB)")
                except (ValueError, IndexError):
                    gpus.append(name) # RAMが取得できない場合
            
            return " / ".join(gpus) if gpus else "N/A"
        except Exception:
            return "N/A"
