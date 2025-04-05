from flask import Flask, render_template, request
from candidate_keys import RelationAnalyzer

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    candidate_keys = []
    attributes = []
    left = right = neither = both = []

    if request.method == 'POST':
        relation_input = request.form['relation']
        dependencies_input = request.form['dependencies']
        attributes = [attr.strip() for attr in relation_input.split(',')]
        dependencies = dependencies_input.replace(' ', '').split(',')

        analyzer = RelationAnalyzer(attributes, dependencies)
        candidate_keys = analyzer.find_candidate_keys()
        left = analyzer.categories.left
        right = analyzer.categories.right
        neither = analyzer.categories.neither
        both = analyzer.categories.both

    return render_template('index.html', 
                           candidate_keys=candidate_keys,
                           attributes=attributes,
                           left=left, right=right,
                           neither=neither, both=both)

if __name__ == '__main__':
    app.run(debug=True)
