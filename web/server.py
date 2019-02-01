""" This module contains the main web interface for bucephawiki. """

from flask import Flask, redirect, url_for, abort, render_template, make_response, request, escape
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from werkzeug import unescape
app = Flask(__name__)

import traceback
from datetime import datetime

import requests
from http import HTTPStatus

import dbops
import config
import fortunes
from render import *

#
# Endpoints
#

# Index endpoint.
@app.route('/')
def index():
  return render_template("index.html", timestamp=datetime.now().strftime("Clock: %A %d %B - %Y/%m/%d %H:%M:%S:%f"),
                         randomse=fortunes.long_fortune(), viewernotes=fortunes.short_fortune(), pinned=get_pinned())


# If we don't specify a view, we probably want the index.
@app.route('/v/')
def noview():
  return redirect(url_for('index'))


# Normal pages
@app.route('/v/page/')
@app.route('/v/page/<path:path>', methods=['POST', 'GET'])
def v_page(path=''):
  if(path == ''):
    path = 'MainPage'

  if not dbops.valid_path(path):
    abort(400)

  if request.method == 'POST':
    if dbops.path_exists(path) and dbops.path_type(path) != dbops.PathType.TEXT:
      abort(405)

    write_wiki(path, request.form['newtext'])

  if not dbops.path_exists(path) and request.args.get('new', 0, type=int) == 0:
    return redirect(url_for('v_page', path=path, edit=1, new=1))

  if dbops.path_type(path) == dbops.PathType.DIRECTORY:
    return render_directory(path)

  if request.args.get('raw', 0, type=int) != 0:
    return render_raw(path)


  if request.args.get('pdf', 0, type=int) != 0:
    return render_pdf(path)
  elif request.args.get('edit', 0, type=int) != 0:
    return render_edit(path, True if (request.args.get('new', 0, type=int) != 0) else False)

  if config.enable_ggb_integration() and path[-4:] == '.gbb':
    return render_geogebra(path)

  if dbops.path_type(path) == dbops.PathType.TEXT:
    return render_wiki(path)

  return render_raw(path)

#
# Pinned
#

def get_pinned():
  return None

#
# Tasklist
#

@app.route('/v/tasks', methods=['POST', 'GET'])
def v_tasks():
  if not config.enable_tasklist_web():
    return abort(403)

  if(request.method == 'POST'):
    if not config.enable_tasklist_web_write():
      return abort(405)
    if 'add' in request.form:
      tasklist.add(request.form['toadd'])
    elif 'todelete' in request.form:
      tasklist.rm(request.form.getlist('delete'))

  return render_template('tasklist.html', tasks=tasklist.tasks(), breadcrumbs = [{'loc': url_for('v_tasks'),'name':'Task list','current':1}],
                         viewernotes=fortunes.short_fortune(), writeable=config.enable_tasklist_web_write())


#
# Error handling
#

@app.route('/v/coffee')
def brew_coffee():
  abort(418)

@app.errorhandler(Exception)
def handle_error(e):
  traceback.print_exc()
  if isinstance(e, RequestRedirect):
    return e
  if isinstance(e, HTTPException):
    if(e.code == 301):
      redirect(e.location)
    if(e.code == 418): # HTTPStatus can't handle HTCPCP errors.
      error = {'code': e.code, 'desc': "I'm a teapot", 'long': 'Any attempt to brew coffee with a teapot should result in the error code "418 I\'m a teapot". The resulting entity body MAY be short and stout.'}
    else:
      error = {'code': e.code, 'desc': HTTPStatus(e.code).phrase, 'long': HTTPStatus(e.code).description}
    return render_template("error.html", error=error), e.code
  else:
    error = {'code': 500, 'desc': HTTPStatus(500).phrase + " (threw exception)", 'long': HTTPStatus(500).description + ": " + str(e)}
    return render_template("error.html", error=error), 500
