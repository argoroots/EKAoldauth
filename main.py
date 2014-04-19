#!/usr/bin/env python

import webapp2
import hashlib
import base64
from datetime import *

from google.appengine.ext import db
from google.appengine.api import users


class Settings(db.Model):
    value  = db.StringProperty(default='', indexed=False)


class Users(db.Model):
    last_login  = db.DateTimeProperty(auto_now=True)
    login_count = db.IntegerProperty(default=0)


class LogIn(webapp2.RequestHandler):
    def get(self):
        login_url = Settings().get_or_insert('login_url')
        logout_url = Settings().get_or_insert('logout_url')
        secret = Settings().get_or_insert('secret')

        user = users.get_current_user()
        if not user:
            return self.redirect(logout_url.value)

        if not user.email():
            return self.redirect(logout_url.value)

        user_key = hashlib.md5(user.email() + (datetime.today() + timedelta(hours=2)).strftime('%Y-%m-%d') + secret.value).hexdigest()
        key = base64.b64encode(user_key + user.email())

        current_user = Users().get_or_insert(user.email())
        current_user.login_count += 1
        current_user.put()

        self.redirect(str(login_url.value % key))


class LogOut(webapp2.RequestHandler):
    def get(self):
        logout_url = Settings().get_or_insert('logout_url')

        user = users.get_current_user()
        if user:
            self.redirect(str(users.create_logout_url(logout_url.value)))
        else:
            self.redirect(str(logout_url.value))


app = webapp2.WSGIApplication([
    ('/login', LogIn),
    ('/logout', LogOut),
], debug=True)
