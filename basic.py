from flask import Flask
#from flask_bootstrap import Bootstrap

app = Flask(__name__)
#Bootstrap(app)

"""
Routes
"""

@app.route('/', methods=['GET'])
def index():
    return "<h1>Hello World</h1>"

if __name__ == '__main__':
    app.run(debug=True)