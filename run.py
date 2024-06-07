
from Demo_web.application.api import account_activation
from Demo_web.application import create_app
from flask import render_template
app = create_app(debug=True)


@app.route("/reset_password/<token>")
def reset_password(token):
    email = account_activation.confirm_reset_token(token)
    if email is False:
        return render_template('404.html'), 404
    else:
        return render_template('reset_password.html', email=email)
    
if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    # eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    app.run(port=5050, debug=True)


