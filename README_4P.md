# 4P分析 スライドジェネレーター

企業名を入力するだけで、AIが自動で4P分析を行い、プロフェッショナルなスライドを生成するアプリケーションです。

## 機能

- **AI自動分析**: OpenAI GPT-4を使用した企業の4P分析
- **美しいスライド**: SVGベースの見やすいデザイン
- **PDF出力**: 生成したスライドをPDF形式でダウンロード可能
- **リアルタイムプレビュー**: ブラウザ上でスライドを即座に確認

## ファイル構成

```
group_5/
├── app_4p.py          # メインアプリケーション（4P分析版）
├── 4P_template.html   # Jinja2テンプレート（4P分析用）
├── requirements.txt   # 必要なライブラリ
└── README_4P.md      # このファイル
```

## セットアップ

### 1. 必要なライブラリをインストール

```bash
pip install streamlit openai jinja2 weasyprint
```

### 2. OpenAI API キーの設定

環境変数に OpenAI API キーを設定してください：

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# macOS/Linux
export OPENAI_API_KEY="your-api-key-here"
```

### 3. アプリケーションの起動

```bash
py -m streamlit run app_4p.py
```

## 使用方法

1. **企業名入力**: テキストボックスに分析したい企業名を入力
2. **分析実行**: 「4P分析スライドを生成」ボタンをクリック
3. **結果確認**: AIが生成した4P分析結果を確認
4. **PDF出力**: 「PDFをダウンロード」ボタンで資料を保存

## Jinja2テンプレートの仕組み

### テンプレート（4P_template.html）
```html
<!-- 企業名の表示 -->
<text>{{ company }} - 4P Analysis</text>

<!-- Product項目の繰り返し表示 -->
{% for item in product_items %}
<text>• {{ item }}</text>
{% endfor %}
```

### Pythonからのデータ渡し（app_4p.py）
```python
# テンプレートにデータを渡す
html_content = template.render(
    company="Apple",
    product_items=["iPhone", "MacBook", "iPad"],
    price_items=["プレミアム価格戦略", "高付加価値"],
    # ...
)
```

## カスタマイズ

### テンプレートのデザイン変更
`4P_template.html` を編集することで、スライドの見た目を変更できます：

- **色の変更**: `fill="#9b443f"` の部分を変更
- **フォントサイズ**: `font-size="20"` の数値を変更  
- **レイアウト**: 座標 `x="100" y="200"` を調整

### プロンプトの改善
`app_4p.py` の `generate_4p_analysis()` 関数内のプロンプトを修正することで、より詳細な分析や特定業界向けの分析が可能です。

## トラブルシューティング

### エラー: "OpenAI API key not found"
- 環境変数 `OPENAI_API_KEY` が正しく設定されているか確認
- APIキーが有効か確認

### エラー: "Template file not found"
- `4P_template.html` が同じディレクトリにあるか確認
- ファイルパスが正しいか確認

### PDFが生成されない
- WeasyPrintの依存関係が正しくインストールされているか確認
- Windows の場合、追加のライブラリが必要な場合があります

## 応用例

- **競合分析**: 複数企業の4P分析を比較
- **業界分析**: 特定業界の企業群を一括分析
- **戦略立案**: 自社の4P戦略検討に活用

---

4P分析（Product, Price, Place, Promotion）は、マーケティング戦略の基本フレームワークです。このツールを使って、効率的に企業分析を行いましょう！ 