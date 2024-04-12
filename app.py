from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    import requests
    url = request.json['url']
    response = requests.get(url)
    return jsonify({"content": response.text})

if __name__ == '__main__':
    app.run(debug=True)

