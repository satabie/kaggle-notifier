# kaggle-notifier

Kaggleの新着コンペティションをメールで通知するツール。テーブルコンペのみをフィルタリングして通知可能。

## 機能

- Kaggle APIを使用してコンペ一覧を取得
- テーブルコンペ（`tabular`タグ）のみをフィルタリング
- カテゴリー（Featured, Researchなど）でフィルタリング
- 送信済みコンペの重複通知を防止
- Gmailを使ったメール通知

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`を作成：

```bash
cp .env.example .env
```

`.env`を編集して以下を設定：

```bash
# 通知先メールアドレス
EMAIL=your-email@example.com

# SMTP設定（Gmailの場合）
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-digit-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Gmailアプリパスワードの取得方法

1. Googleアカウントで2段階認証を有効化
2. [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) にアクセス
3. アプリパスワードを生成（16桁の英数字）
4. `SMTP_PASS`に設定（スペースなし）

### 3. Kaggle API認証の設定

Kaggle APIの認証情報が必要です：

1. [Kaggle Account Settings](https://www.kaggle.com/settings/account) にアクセス
2. "Create New Token"をクリックして`kaggle.json`をダウンロード
3. `~/.kaggle/kaggle.json`に配置

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 4. フィルター設定

`config.json.example`をコピーして`config.json`を作成：

```bash
cp config.json.example config.json
```

`config.json`を編集：

```json
{
  "filters": {
    "table_only": true,
    "category": ["Featured", "Research"]
  }
}
```

#### フィルターオプション

- `table_only`: `true`にするとテーブルコンペ（`tabular`タグ）のみ通知
- `category`: 通知対象のカテゴリーを指定（例：`["Featured", "Research"]`）
  - `Featured`: 企業スポンサー付きコンペ
  - `Research`: 研究目的のコンペ
  - `Getting Started`: 初心者向けチュートリアル（メダル対象外）

## 使い方

```bash
uv run python main.py
```

## 定期実行（GitHub Actions）

GitHub Actionsを使って毎日自動で新着コンペをチェックできます。

### GitHub Actionsの設定手順

1. **リポジトリのSecretsを設定**

   GitHubリポジトリの `Settings` > `Secrets and variables` > `Actions` > `New repository secret` で以下を追加：

   | Secret名 | 値 | 説明 |
   |---------|---|------|
   | `EMAIL` | `your-email@example.com` | 通知先メールアドレス |
   | `SMTP_USER` | `your-email@gmail.com` | SMTP認証用メールアドレス |
   | `SMTP_PASS` | `your-app-password` | Gmailアプリパスワード（16桁） |
   | `KAGGLE_USERNAME` | `your-kaggle-username` | Kaggleユーザー名 |
   | `KAGGLE_KEY` | `your-kaggle-api-key` | Kaggle APIキー |

2. **Kaggle認証情報の取得**

   - [Kaggle Account Settings](https://www.kaggle.com/settings/account) にアクセス
   - "Create New Token"をクリックして`kaggle.json`をダウンロード
   - ファイルを開いて`username`と`key`の値をコピー

3. **GitHub Actionsを有効化**

   - リポジトリの `Actions` タブを開く
   - ワークフローが表示されることを確認

4. **手動実行でテスト**

   - `Actions` タブ > `Kaggle Notifier` を選択
   - `Run workflow` ボタンをクリックして手動実行

### スケジュール

- **デフォルト**: 毎日 9:00 AM UTC（日本時間 18:00）に実行
- **変更方法**: [.github/workflows/notify.yml](.github/workflows/notify.yml) の `cron` を編集

```yaml
schedule:
  # 毎日 0:00 UTC（日本時間 9:00）に変更する場合
  - cron: '0 0 * * *'
```

### 送信履歴の管理

- GitHub Actionsのキャッシュ機能を使用して`sent_competitions.json`を保持
- 重複通知を防止

## ファイル構成

```
.
├── main.py                    # メインスクリプト
├── config.json.example        # 設定ファイルのテンプレート
├── .env.example               # 環境変数のテンプレート
├── sent_competitions.json     # 送信済みコンペの履歴（自動生成）
├── pyproject.toml             # 依存パッケージ管理
└── README.md                  # このファイル
```

## トラブルシューティング

### SMTP認証エラー

```
SMTPAuthenticationError: Username and Password not accepted
```

- Gmailの2段階認証が有効になっているか確認
- アプリパスワード（通常のパスワードではない）を使用しているか確認
- `SMTP_PASS`にスペースが含まれていないか確認

### Kaggle API認証エラー

```
OSError: Could not find kaggle.json
```

- `~/.kaggle/kaggle.json`が存在するか確認
- ファイルのパーミッションが`600`になっているか確認（`chmod 600 ~/.kaggle/kaggle.json`）

## ライセンス

MIT
