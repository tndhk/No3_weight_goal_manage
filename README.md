# React-Flask-SQLite アプリケーション

個人開発用のWebアプリケーションテンプレートです。React、Flask、SQLiteを使用したフルスタックアプリケーションで、Docker環境で開発が可能です。

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

### データベース
- SQLite

### 開発環境
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- MacBook M2環境最適化

## 開発環境のセットアップ

### 必要条件
- Docker Desktop
- Git

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/my-react-flask-app.git
cd my-react-flask-app
```

2. Docker Composeでアプリケーションを起動
```bash
docker-compose up
```

3. ブラウザでアクセス
   - フロントエンド: http://localhost:3000
   - バックエンドAPI: http://localhost:5000

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

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。