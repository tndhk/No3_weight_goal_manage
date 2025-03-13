# React-Flask-SQLite アプリケーション

個人開発用のWebアプリケーションテンプレートです。React、Flask、SQLiteを使用したフルスタックアプリケーションで、Docker環境で開発が可能です。Fitbit API連携機能を備え、体重データの取得・分析が可能です。

## 技術スタック

### フロントエンド
- React 18
- React Router
- Chart.js (React-ChartJS-2)
- Axios

### バックエンド
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- Marshmallow
- Requests (外部API連携)

### データベース
- SQLite

### 外部API連携
- Fitbit API (OAuth2.0認証)

### 開発環境
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- MacBook M2環境最適化

## 開発環境のセットアップ

### 必要条件
- Docker Desktop
- Git
- Fitbit Developer アカウント (APIアクセス用)

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/my-react-flask-app.git
cd my-react-flask-app
```

2. Fitbit Developer Portalでアプリケーションを登録
   - https://dev.fitbit.com/apps/new にアクセス
   - 必要情報を入力し、OAuth 2.0コールバックURLを `http://localhost:5000/api/fitbit/callback` に設定
   - クライアントIDとクライアントシークレットを取得

3. 環境変数の設定
```bash
cp backend/.env.example backend/.env
```
- `.env` ファイルを編集して、Fitbit APIのクライアントIDとシークレットを設定

4. Docker Composeでアプリケーションを起動
```bash
docker-compose up
```

5. ブラウザでアクセス
   - フロントエンド: http://localhost:3000
   - バックエンドAPI: http://localhost:5000

## 機能一覧

### 基本機能
- データ追加・編集・削除
- データ分析・可視化

### Fitbit API連携機能
- OAuth2.0認証によるFitbitアカウント連携
- 体重データの取得と表示
- 体重変化の分析とグラフ表示

## プロジェクト構造

```
project-root/
│
├── frontend/          # Reactアプリケーション
├── backend/           # Flaskアプリケーション
└── docker-compose.yml # Docker設定
```

## 開発ワークフロー

1. 機能ブランチを作成
```bash
git checkout -b feature/new-feature
```

2. 変更を実装

3. 変更をコミット
```bash
git add .
git commit -m "Add new feature"
```

4. GitHubにプッシュ
```bash
git push origin feature/new-feature
```

5. Pull Requestを作成

## Fitbit API連携の設定

1. Fitbit Developer PortalでのOAuth 2.0アプリ登録
2. 取得したクライアントIDとシークレットを環境変数に設定
3. 必要なスコープの指定 (現在は体重データ用のスコープを使用)

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。