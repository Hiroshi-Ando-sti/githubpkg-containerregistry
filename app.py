from flask import Flask

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# '/'へのGETリクエストに対するルートを定義
@app.route('/')
def hello():
    return "Hello, Python Docker on GitHub Packages!\n"

# '/test'へのGETリクエストに対するルートを定義
@app.route('/test')
def test():
    return "Hello, test endpoint!\n"

# このファイルが直接実行された場合にのみサーバーを起動（ローカルテスト用）
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)