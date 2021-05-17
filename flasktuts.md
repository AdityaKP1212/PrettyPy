#intro
- pip install flask
- import flask
- register app

#routing
- use app.route decorator and specify path in param
- return html from function

#run
- if main then run

#jinja templating used in template
- {% block%} {%endblock%} start and end blocks [for, if, header, footer, content]
- {{ data/functions }} use objects or data or functions

#methods
- specify in get and post in decorator

#forms
- on post call (request.method == POST) get form content using id request.form['#id']


#pass data to template
- in render_template pass data as context

#run app
- python app.py