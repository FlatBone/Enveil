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
                info["GPU"] = self._get_windows_gpu_info()
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

    def _get_windows_gpu_info(self) -> str:
        """
        WindowsのGPU情報を収集する。4.0GBの制限を考慮し、まずnvidia-smiを試行し、失敗した場合はwmicにフォールバックする。
        """
        # 1. Try nvidia-smi first
        try:
            gpu_names_raw = self.executor.execute("get_gpu_name_nvidia")
            gpu_mems_raw = self.executor.execute("get_gpu_mem_nvidia")
            
            names = [name.strip() for name in gpu_names_raw.strip().splitlines()]
            mems_mib = [int(mem.strip()) for mem in gpu_mems_raw.strip().splitlines()]

            if len(names) != len(mems_mib):
                 raise ValueError("Mismatch between GPU names and memory info from nvidia-smi.")

            gpus = []
            for name, mem_mib in zip(names, mems_mib):
                # nvidia-smi provides MiB (1024*1024 bytes). Convert to GiB for the "GB" display.
                mem_gb = mem_mib / 1024
                gpus.append(f"{name} ({mem_gb:.1f}GB)")
            
            return " / ".join(gpus) if gpus else "N/A"

        except Exception:
            # 2. Fallback to wmic
            gpu_raw = self.executor.execute("get_gpu_windows")
            return self._format_gpu_windows(gpu_raw)

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
                gpu_name = parts[name_index].strip()
                ram_str = parts[ram_index].strip()
                
                try:
                    ram_bytes_signed = int(ram_str)
                    
                    if ram_bytes_signed < 0:
                        # Handle potential 32-bit signed integer overflow for > 2GB VRAM
                        ram_bytes = ram_bytes_signed + 2**32
                    else:
                        ram_bytes = ram_bytes_signed

                    if ram_bytes > 0:
                        ram_gb = ram_bytes / (1024**3)
                        gpus.append(f"{gpu_name} ({ram_gb:.1f}GB)")
                    else:
                        gpus.append(gpu_name)
                except (ValueError, IndexError):
                    # If RAM is not a valid number, just append the name
                    gpus.append(gpu_name)
            
            return " / ".join(gpus) if gpus else "N/A"
        except Exception:
            return "N/A"