from flask import Flask
from app import app

from flask_wtf.csrf import CSRFProtect

app.secret_key = '6dbf23122cb5046cc5c0c1b245c75f8e43c59ca8ffeac292715e5078e631d0c9'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  


@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; \
        style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; \
        script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; \
        font-src 'self' https://fonts.gstatic.com"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'same-origin'
    return response

csrf = CSRFProtect(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)