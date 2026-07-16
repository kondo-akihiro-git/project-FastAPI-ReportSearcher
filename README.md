# 週報検索システム（ReportSearcher）
 
## アプリ概要
このアプリは、**社内ポータルに投稿された週報を横断的に検索できる**Webアプリです。  
社内ポータルへのログイン情報を登録しておくことで、定期的に週報を自動取得し、  
キーワード検索によって過去の週報を素早く探し出すことができます。  
毎回ポータルにログインして個別に週報を探す手間をなくし、社内の情報共有・過去実績の参照を効率化します。
 
<br>
主な機能
- ログイン情報登録（社内ポータルの認証情報を保存）
- 社内ポータルからの週報自動取得
- キーワードによる週報検索
- 検索結果の一覧表示
---
 
## 主な画面
- `ログイン画面` : 社内ポータルへのログイン情報登録画面
<kbd><img width="600" height="400" alt="login" src="https://placehold.jp/600x400.png?text=login" /></kbd>
</br></br>

- `過去の週報確認画面` : 取得済み週報の一覧確認画面
<kbd><img width="600" height="400" alt="report" src="https://placehold.jp/600x400.png?text=report" /></kbd>
</br></br>

- `検索画面` : キーワードによる週報検索画面
<kbd><img width="600" height="400" alt="search" src="https://placehold.jp/600x400.png?text=search" /></kbd>
</br></br>

 
---
 
## フォルダ構成
- `backend/`
  - `api/`
    - `main.py` : FastAPIエントリポイント
  - `batch/`
    - `scraper.py` : 社内ポータルからの週報スクレイピング処理
  - `logic/`
    - `login.py` : ログイン情報登録ロジック
    - `register.py` : 週報登録ロジック
    - `search.py` : キーワード検索ロジック
    - `check.py` : 各種チェック処理
    - `runner.py` : バッチ実行ロジック
  - `model/`
    - `models.py` : データモデル定義
  - `data/`
    - `login/` : ログイン情報保存先
    - `report/` : 取得済み週報保存先
  - `requirements.txt` : 依存ライブラリ定義
- `frontend/`
  - `src/`
    - `App.tsx` : アプリルートコンポーネント
    - `main.tsx` : エントリポイント
    - `pages/` : 各画面コンポーネント
  - `package.json` : 依存ライブラリ定義
  - `vite.config.ts` : Vite設定
---
 
## 主な技術要件
 
### リリース時
- Python : バックエンド実装
- FastAPI : APIフレームワーク
- React(TypeScript) : フロントエンド実装
- AWS Lambda : API実行環境
- Amazon S3 : フロントエンド静的ファイル配信・データ保存
- Amazon CloudFront : CDN配信
- Amazon EventBridge : 週報取得バッチの定期実行
### ローカル開発時
- Python : バックエンド実装
- FastAPI : APIフレームワーク
- React(TypeScript) : フロントエンド実装
---
 
## デプロイ手順
このアプリは **AWS（S3 / CloudFront / Lambda / EventBridge）** にデプロイしています。
手順は以下の通りです。
1. フロントエンドをビルド（`npm run build`）し、成果物をS3にアップロード
2. CloudFrontよりS3を配信し、静的サイトとして公開
3. バックエンド（FastAPI）をAWS Lambda用にパッケージング
4. Lambda関数としてデプロイし、API Gateway等と連携
5. EventBridgeにて週報取得バッチ（scraper）の定期実行ルールを設定
6. 動作確認後、公開完了
