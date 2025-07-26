# 設計文書

## 概要

クロスプラットフォーム環境取得ツール「Enveil」は、Windows、macOS、Linux上で統一されたインターフェースを通じてシステム情報を収集するPythonライブラリです。

## アーキテクチャ

### 全体構成

```
enveil/
├── __init__.py          # パッケージエントリーポイント
├── main.py              # メイン実行ファイル
├── core/
│   ├── __init__.py
│   ├── platform_detector.py    # プラットフォーム検出
│   ├── command_executor.py     # セキュアなコマンド実行
│   └── data_formatter.py       # データ整形
├── collectors/
│   ├── __init__.py
│   ├── base_collector.py       # 基底クラス
│   ├── hardware_collector.py   # ハードウェア情報収集
│   ├── os_collector.py         # OS情報収集
│   └── software_collector.py   # ソフトウェア情報収集
├── config/
│   ├── __init__.py
│   ├── config_manager.py       # 設定管理
│   └── default_software.py     # デフォルトソフトウェア定義
└── utils/
    ├── __init__.py
    ├── security.py             # セキュリティ関連ユーティリティ
    └── exceptions.py            # カスタム例外
```

### レイヤー構成

1. **プレゼンテーション層**: CLI インターフェース（main.py）
2. **アプリケーション層**: 情報収集オーケストレーション
3. **ドメイン層**: 各種コレクター（hardware, os, software）
4. **インフラストラクチャ層**: プラットフォーム固有の実装、コマンド実行

## コンポーネントと インターフェース

### 1. PlatformDetector

プラットフォーム検出と適切なコマンド選択を担当します。

```python
class PlatformDetector:
    @staticmethod
    def get_platform() -> str
    @staticmethod
    def is_windows() -> bool
    @staticmethod
    def is_linux() -> bool
    @staticmethod
    def is_macos() -> bool
```

### 2. CommandExecutor

セキュアなコマンド実行を担当します。インジェクション攻撃を防ぐため、許可されたコマンドパターンのみを実行します。

```python
class CommandExecutor:
    def __init__(self, allowed_commands: Dict[str, List[str]])
    def execute(self, command_key: str, params: List[str] = None) -> str
    def is_command_safe(self, command: str) -> bool
    def sanitize_input(self, input_str: str) -> str
```

### 3. BaseCollector

全ての情報収集クラスの基底クラスです。

```python
class BaseCollector:
    def __init__(self, executor: CommandExecutor)
    def collect(self) -> Dict[str, Any]
    def is_available(self) -> bool
```

### 4. HardwareCollector

ハードウェア情報（CPU、RAM、GPU）を収集します。

```python
class HardwareCollector(BaseCollector):
    def collect_cpu_info(self) -> str
    def collect_ram_info(self) -> str
    def collect_gpu_info(self) -> str
    def format_ram_size(self, raw_size: str) -> str
```

### 5. OSCollector

OS情報を収集します。

```python
class OSCollector(BaseCollector):
    def collect_os_info(self) -> str
    def get_windows_info(self) -> str
    def get_linux_info(self) -> str
    def get_macos_info(self) -> str
```

### 6. SoftwareCollector

ソフトウェアバージョン情報を収集します。

```python
class SoftwareCollector(BaseCollector):
    def __init__(self, executor: CommandExecutor, config_manager: ConfigManager)
    def collect_software_versions(self, software_list: List[str] = None) -> Dict[str, str]
    def get_default_software(self) -> Dict[str, str]
```

### 7. ConfigManager

設定ファイルの管理を担当します。

```python
class ConfigManager:
    def __init__(self, config_path: str = "config.json")
    def load_config(self) -> Dict[str, Any]
    def get_software_commands(self) -> Dict[str, str]
    def validate_config(self, config: Dict[str, Any]) -> bool
```

### 8. EnveilAPI

ライブラリとしての主要APIを提供します。

```python
class EnveilAPI:
    def __init__(self, config_path: str = None)
    def get_all_info(self) -> Dict[str, Any]
    def get_hardware_info(self) -> Dict[str, str]
    def get_os_info(self) -> str
    def get_software_info(self, software_list: List[str] = None) -> Dict[str, str]
```

## データモデル

### 情報収集結果の構造

```python
@dataclass
class SystemInfo:
    hardware: Optional[HardwareInfo] = None
    os: Optional[str] = None
    software: Optional[Dict[str, str]] = None

@dataclass
class HardwareInfo:
    cpu: str
    ram: str
    gpu: str

@dataclass
class SoftwareInfo:
    name: str
    version: str
    status: str  # "installed", "not_found", "error"
```

### 設定ファイル構造

```json
{
  "software": {
    "Python": "python --version",
    "Git": "git --version",
    "Docker": "docker --version",
    "Node.js": "node -v",
    "CustomTool": "customtool --version"
  },
  "security": {
    "allowed_command_patterns": [
      "^(python|python3) --version$",
      "^git --version$",
      "^docker --version$",
      "^node -v$"
    ],
    "blocked_characters": [";", "&", "|", "`", "$", "(", ")"]
  }
}
```

## エラーハンドリング

### カスタム例外階層

```python
class EnveilException(Exception):
    """基底例外クラス"""
    pass

class CommandExecutionError(EnveilException):
    """コマンド実行エラー"""
    pass

class SecurityError(EnveilException):
    """セキュリティ関連エラー"""
    pass

class ConfigurationError(EnveilException):
    """設定エラー"""
    pass

class PlatformNotSupportedError(EnveilException):
    """サポートされていないプラットフォーム"""
    pass
```

### エラー処理戦略

1. **グレースフルデグラデーション**: 一部の情報が取得できなくても、取得可能な情報は返す
2. **詳細ログ**: デバッグ用の詳細なエラー情報をログに記録
3. **ユーザーフレンドリーメッセージ**: エンドユーザーには分かりやすいエラーメッセージを表示
4. **フォールバック**: プライマリコマンドが失敗した場合の代替手段

## テスト戦略

### テストレベル

1. **ユニットテスト**: 各コンポーネントの個別機能テスト
2. **統合テスト**: コンポーネント間の連携テスト
3. **システムテスト**: 実際の環境での動作テスト
4. **セキュリティテスト**: インジェクション攻撃の防御テスト

### テスト対象

#### ユニットテスト
- CommandExecutor のセキュリティ機能
- 各Collector の情報収集ロジック
- ConfigManager の設定読み込み
- データフォーマッター の変換処理

#### 統合テスト
- プラットフォーム固有のコマンド実行
- 設定ファイルと実際のソフトウェア検出の連携
- エラーハンドリングの動作

#### セキュリティテスト
- コマンドインジェクション攻撃の防御
- 不正な設定ファイルの処理
- 特殊文字を含む入力の処理

### モックとスタブ

```python
class MockCommandExecutor:
    """テスト用のコマンド実行モック"""
    def __init__(self, responses: Dict[str, str])
    def execute(self, command_key: str, params: List[str] = None) -> str

class TestDataProvider:
    """テスト用のサンプルデータ提供"""
    @staticmethod
    def get_sample_hardware_info() -> Dict[str, str]
    @staticmethod
    def get_sample_os_info() -> str
    @staticmethod
    def get_sample_software_info() -> Dict[str, str]
```

## セキュリティ考慮事項

### コマンドインジェクション対策

1. **許可リスト方式**: 事前定義されたコマンドパターンのみ実行
2. **入力サニタイゼーション**: 特殊文字の除去・エスケープ
3. **パラメータ化実行**: シェル経由ではなく直接プロセス実行
4. **権限最小化**: 必要最小限の権限でコマンド実行

### 設定ファイルセキュリティ

1. **スキーマ検証**: JSON スキーマによる設定ファイル検証
2. **パス検証**: 実行可能ファイルのパス検証
3. **権限チェック**: 設定ファイルの読み取り権限確認

### 実装例

```python
class SecurityValidator:
    BLOCKED_PATTERNS = [
        r'[;&|`$()]',  # シェルメタ文字
        r'\.\./',      # ディレクトリトラバーサル
        r'rm\s+',      # 危険なコマンド
        r'del\s+',     # 危険なコマンド
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> bool:
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, command):
                return False
        return True
```

## パフォーマンス考慮事項

### 最適化戦略

1. **並列実行**: 独立した情報収集の並列化
2. **キャッシュ**: 重い処理結果のキャッシュ
3. **遅延読み込み**: 必要な情報のみ収集
4. **タイムアウト**: 長時間実行されるコマンドのタイムアウト

### 実装例

```python
import concurrent.futures
from functools import lru_cache

class ParallelCollector:
    def collect_all_info(self, include_hardware=True, include_os=True, include_software=True):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            if include_hardware:
                futures['hardware'] = executor.submit(self.hardware_collector.collect)
            if include_os:
                futures['os'] = executor.submit(self.os_collector.collect)
            if include_software:
                futures['software'] = executor.submit(self.software_collector.collect)
            
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=30)
                except concurrent.futures.TimeoutError:
                    results[key] = f"{key}情報の取得がタイムアウトしました"
            
            return results
```

## 既存コードからの移行戦略

### フェーズ1: リファクタリング
- 既存の main.py を新しいアーキテクチャに適合
- セキュリティ機能の追加
- エラーハンドリングの改善

### フェーズ2: モジュール化
- 機能別のモジュール分割
- テストの追加
- 設定管理の改善

### フェーズ3: ライブラリ化
- API の整備
- ドキュメントの充実
- パッケージング の改善