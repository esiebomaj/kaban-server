import schema
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


app.add_url_rule('/graphql', view_func=schema.graphql_view,
                 methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
