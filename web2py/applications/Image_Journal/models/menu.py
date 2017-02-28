# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('image',SPAN('J'),'ournal'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Onkar Verma and Raghav Gupta'
response.meta.description = 'Recepie App'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
if auth.user ==None:
    response.menu = [
    (T('Home'), False, URL('default', 'index'),[]),
    (T('New'), False, URL('default', 'upload')),
    (T('My Profile'), False, URL('default','profile',args=1)),
    (T('Search'), False, URL('search_result')),
    (T('reports'), False, URL('rep'))

    ]
else:
    response.menu = [
    (T('Home'), False, URL('default', 'index'),[]),
    (T('New'), False, URL('default', 'upload')),
    (T('My Profile'), False, URL('default','profile',args=auth.user.id)),
    (T('Search'), False, URL('search_result')),
    (T('reports'), False, URL('rep'))

    ]


DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
