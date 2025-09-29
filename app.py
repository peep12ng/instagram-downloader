from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World! Flask 서버가 실행 중입니다."

if __name__ == '__main__':
    app.run(debug=True)