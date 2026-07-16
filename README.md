# 週報検索システム（ReportSearcher）
 
## 概要
このアプリは、**社内ポータルに保存された週報でキーワード検索できる**Webアプリです。  
キーワード検索によって過去の週報を探し出すことができます。  
 
<br>
主な機能
- 社内ポータルからの週報取得
- キーワードによる週報検索
- 検索結果の一覧表示
---
 
## 主な画面
- `ログイン画面` : 社内ポータルへのログイン画面
<kbd><img width="734" height="541" alt="login" src="https://github.com/user-attachments/assets/84b21299-d673-4622-bba1-8bf794c1d95c" /></kbd>
</br></br>


- `週報の収集確認画面` : 過去の週報のテキストデータとして収集できるか確認する画面
<kbd><img width="736" height="189" alt="progress" src="https://github.com/user-attachments/assets/a2f908ae-f69f-4eaf-99b4-99a467a3f358" /></kbd>
</br></br>


- `検索画面` : キーワードによる週報検索画面
<kbd><img width="734" height="682" alt="search" src="https://github.com/user-attachments/assets/0f49845d-9c4a-4d26-9719-f3e129110b6e" /></kbd>
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
    - `runner.py` : コマンド実行ロジック
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

### ローカル開発時
- Python : バックエンド実装
- FastAPI : APIフレームワーク
- React(TypeScript) : フロントエンド実装

### リリース時
- AWS Lambda : API実行環境
- Amazon S3 : フロントエンド静的ファイル配信・データ保存
- Amazon CloudFront : CDN配信

---
 
## デプロイ手順
このアプリは **AWS（S3 / CloudFront / Lambda）** に以下の手順でデプロイしています。
1. フロントエンドをビルド（`npm run build`）し、成果物をS3にアップロード
2. CloudFrontよりS3を配信し、静的サイトとして公開
3. バックエンド（FastAPI）をAWS Lambda用にパッケージング
4. Lambda関数としてデプロイ
5. 公開完了
