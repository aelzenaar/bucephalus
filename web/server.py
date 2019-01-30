from flask import Flask, redirect, url_for, abort, render_template, make_response, request, escape
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from werkzeug import unescape
app = Flask(__name__)

import sys
import traceback

import requests
from http import HTTPStatus

import calendar
import magic
from datetime import datetime
import random

import dbops
import config
import search
import tasklist
import fortunes

# Return a link to the pinned article from the database, or None if it doesn't exist.
def get_pinned():
  pinnedid = dbops.get_pinned()
  if pinnedid == None:
    return None

  pinned = dbops.get_record_by_id(pinnedid)
  return {'loc': url_for('v_raw', ident=pinned.doc_id), 'name': menu_name_for_item(pinned)}


def timestamp_for_item(item):
  f = lambda y, m, d, h, n, s: str(y) + str('/') + str(m).zfill(2) + str('/') + str(d).zfill(2) + ' @ ' +\
                          str(h).zfill(2) + ":" + str(n).zfill(2) + ":" + str(s).zfill(2)

  timestamp = f(item['ts_year'], item['ts_month'], item['ts_day'], item["ts_hour"], item['ts_minute'], item['ts_second'])

  if('ts_year2' in item):
    modified  = f(item['ts_year2'], item['ts_month2'], item['ts_day2'], item["ts_hour2"], item['ts_minute2'], item['ts_second2'])
  else:
    modified = timestamp

  return timestamp,modified

def menu_name_for_item(item):
  return item['Buc_name'] + " (modified: "+ timestamp_for_item(item)[1] + "); tags: " + human_readable_tags(item['Buc_tags'])

def human_readable_tags(tags):
  tags = ['\"{0}\"'.format(tag) for tag in tags]
  nice_tag_list = ""
  if len(tags) == 1:
    nice_tag_list = tags[0]
  else:
    for tag in tags[:-1]:
      nice_tag_list = nice_tag_list + tag + ", "
    nice_tag_list = nice_tag_list + " and " + tags[-1]
  return nice_tag_list

# Render a specific article from its database entry, given the set of breadcrumbs you want to display.
def render_article(item, breadcrumbs):
  if (config.enable_ggb_integration()) and (item['Buc_name'][-4:] == '.ggb'):
    rawname = url_for('r_ggb', ident=str(item.doc_id), meat=item['Buc_name'])
    source = url_for('r_file', ident=str(item.doc_id), meat=item['Buc_name'])
  else:
    rawname = url_for('r_file', ident=str(item.doc_id), meat=item['Buc_name'])
    source = url_for('r_file', ident=str(item.doc_id), meat='src', src=item['Buc_source']) if 'Buc_source' in item else None

  tags = []
  for tag in item['Buc_tags']:
    tags.append({'name': str(escape(tag)).replace(' ', '&nbsp;'), 'loc': "/v/tag/" + tag})
  timestamp, modified = timestamp_for_item(item)

  return render_template('article.html', article_name=item['Buc_name'], article_timestamp=timestamp, article_title=item['Buc_title'],
                         article_raw=rawname, article_src=source, article_author=item['Buc_author'], article_id=item.doc_id, tags=tags,
                         breadcrumbs=breadcrumbs, article_modded=modified, viewernotes=fortunes.short_fortune())

@app.route('/r/ggb/<ident>/<meat>')
def r_ggb(ident=None,meat=None):
  if (ident == None) | (meat == None):
    return redirect(url_for('index'))

  if not(meat[-4:] == '.ggb'):
    return abort(415)

  return render_template("ggbframe.html", ggbfilename=url_for('r_file', ident=ident, meat=meat))

# Endpoint to pull a specific raw file (i.e. no UI) out of the database.
@app.route('/r/')
@app.route('/r/<ident>/')
@app.route('/r/<ident>/<meat>')
@app.route('/r/<ident>/<meat>/<src>')
def r_file(ident=None,meat=None,src=None):
  if (ident == None) | (meat == None):
    return redirect(url_for('index'))

  if(meat == 'src'):
    filename = dbops.get_single_record_src_path(ident,src)
  else:
    filename = dbops.get_single_record_path(ident,meat)
  if(filename == None):
    return abort(404)
  with filename.open(mode='rb') as f:
    data = f.read()

  resp = make_response(data)
  # Fudge the mimetypes
  mime = magic.Magic(mime=True).from_file(str(filename))
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  return resp

# Index endpoint.
@app.route('/')
def index():
  return render_template("index.html", timestamp=datetime.now().strftime("Clock: %A %d %B - %Y/%m/%d %H:%M:%S:%f"),
                         randomse=fortunes.long_fortune(), viewernotes=fortunes.short_fortune(), pinned=get_pinned())

# If we don't specify a view, we probably want the index.
@app.route('/v/')
def noview():
  return redirect(url_for('index'))

# View in a temporal fashion, up to the day granularity.
@app.route('/v/time/')
@app.route('/v/time/<year>/')
@app.route('/v/time/<year>/<month>/')
@app.route('/v/time/<year>/<month>/<day>/')
@app.route('/v/time/<year>/<month>/<day>/<meat>/')
def v_time(year=None,month=None,day=None,meat=None):
  items = []
  if(year == None):
    years = dbops.get_records_by_date()
    if not years:
      abort(404)
    for year in years:
      items.append({'loc': url_for('v_time', year=str(year)), 'name': year})
    return render_template('viewer.html',items=items,view_name='year', breadcrumbs=[{'loc':url_for('v_time'),'name':'By date', 'current':1}], viewernotes=fortunes.short_fortune())

  if(month == None):
    months = dbops.get_records_by_date(year)
    if not months:
      abort(404)
    for month in months:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month)),'name':calendar.month_name[int(month)]},
                           breadcrumbs=[{'loc':url_for('v_time'), 'name': 'By date'},
                                        {'loc':url_for('v_time', year=str(year)),'name': year, 'current':1}], viewernotes=fortunes.short_fortune())

  if(day == None):
    days = dbops.get_records_by_date(year, month)
    for day in days:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': day})
    if not days:
      abort(404)
    return render_template('viewer.html',items=items,view_name='day',
                           breadcrumbs=[{'loc': url_for('v_time'), 'name': 'By date'},
                                        {'loc': url_for('v_time', year=str(year)), 'name': year},
                                        {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)], 'current':1}],
                           viewernotes=fortunes.short_fortune())

  if(meat == None):
    docs = dbops.get_records_by_date(year, month, day)
    if not docs:
      abort(404)
    for doc in docs:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month), day=str(day), meat=doc['Buc_name']),
                    'name': menu_name_for_item(doc)})
    return render_template('viewer.html',items=items,view_name='article',
                           breadcrumbs=[{'loc': url_for('v_time'), 'name': 'By date'},
                                        {'loc': url_for('v_time', year=str(year)), 'name': year},
                                        {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)]},
                                        {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': str(day), 'current':1}],
                           viewernotes=fortunes.short_fortune())

  item = dbops.get_records_by_date(year, month, day, meat)
  if(item == None):
    return abort(404)

  return render_article(item, [{'loc': url_for('v_time'), 'name': 'By date'},
                               {'loc': url_for('v_time', year=str(year)), 'name': year},
                               {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)]},
                               {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': str(day)},
                               {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day), meat=meat), 'name':meat, 'current':1}])

# Endpoint to handle search-by-ID. Redirects back to the main endpoint.
@app.route('/v/raw/post', methods=['POST'])
def v_raw_post():
  return redirect(url_for('v_raw', ident = request.form['ident']))

# Main endpoint for search-by-ID
@app.route('/v/raw/')
@app.route('/v/raw/<ident>/')
def v_raw(ident=None):
  if not (ident == None):
    item = dbops.get_record_by_id(ident)
    if(item == None):
      return abort(404)
    else:
      return render_article(item, [{'loc': url_for('v_raw'), 'name': 'By ID'},
                                   {'loc': url_for('v_raw', ident=str(ident)), 'name':ident, 'current':1}])

  return render_template("v_raw.html",
                         viewernotes=fortunes.short_fortune())

@app.route('/v/tag/')
@app.route('/v/tag/<path:tags>')
@app.route('/v/tag/<path:tags>/<ident>/<meat>')
def v_tag(tags=None, ident=None, meat=None):
  items = []
  if(tags == None):
    tags = dbops.get_records_by_tag()
    if not tags:
      abort(404)
    for tag in tags:
      items.append({'loc': url_for('v_tag', tags=tag), 'name': tag})
    return render_template('viewer.html',items=items, view_name='tag', breadcrumbs=[{'loc':url_for('v_tag'),'name':'By tag', 'current':1}],
                           viewernotes=fortunes.short_fortune())

  tags = tags.split('/')
  nice_tag_list = human_readable_tags(tags)

  if (ident == None):
    docs = dbops.get_records_by_tag(tags)
    if not docs:
      abort(404)
    for doc in docs:
      items.append({'loc': url_for('v_tag', tags="/".join(tags), ident=doc.doc_id, meat=doc['Buc_name']),
                    'name': menu_name_for_item(doc)})
    return render_template('viewer.html', items=items, view_name='tag',
                           breadcrumbs=[{'loc':url_for('v_tag'),'name':'By tag'},
                                        {'loc':url_for('v_tag', tags="/".join(tags)), 'name': nice_tag_list, 'current':1}],
                           viewernotes=fortunes.short_fortune())

  item = dbops.get_record_by_id(ident)
  if(item == None):
    return abort(404)
  if not(item['Buc_name'] == meat):
    return abort(404)

  return render_article(item, [{'loc': url_for('v_tag'),'name':'By tag'},
                               {'loc': url_for('v_tag', tags="/".join(tags)), 'name': nice_tag_list},
                               {'loc': url_for('v_tag', tags="/".join(tags), ident=item.doc_id, meat=item['Buc_name']), 'name':meat, 'current':1}])
  return abort(501)

@app.route('/v/recent/')
def v_recent():
  items = []
  ids = dbops.get_recents()
  for i in ids:
    doc = dbops.get_record_by_id(i)
    items.append({'loc': url_for('v_time', year=doc['ts_year'], month=doc['ts_month'],day=doc['ts_day'],meat=doc['Buc_name']), 'name': menu_name_for_item(doc)})

  return render_template('viewer.html',items=items, view_name='recent', breadcrumbs=[{'loc':url_for('v_recent'),'name':'By recent', 'current':1}],
                          viewernotes=fortunes.short_fortune())

  return abort(501)


# Obsolete
@app.route('/v/grep/post')
def v_grep_obsolete():
  return abort(410)

# Main endpoint for search-by-ID
@app.route('/v/grep/')
def v_grep():
  q = request.args.get('q', '')
  if q == '':
    return render_template("v_grep.html", searchtype="initial", viewernotes=fortunes.short_fortune())

  # So we have a query to search.
  caseSensitive = request.args.get('c', False, bool)
  files = search.search_files_for_string(q, caseSensitive)

  items = []
  for f in files:
    parts = f.relative_to(config.get_user_data_dir()).parts
    if len(parts) < 4:
      continue
    year = parts[0]
    month = parts[1]
    day = parts[2]
    if(str(parts[3]) == 'src'):
      meat = parts[4]
    else:
      meat = parts[3]
    item = dbops.get_record_by_file(year, month, day, meat)
    if not(item == None):
      items.append({'loc': url_for('v_grep_viewer', q=q, ident=item.doc_id, meat=item['Buc_name']), 'name': menu_name_for_item(item)})
  if (items == []):
    return render_template("v_grep.html", searchtype="empty", q=q, viewernotes=fortunes.short_fortune())

  return render_template('viewer.html', items=items, view_name='grep',
                                        breadcrumbs = [{'loc': url_for('v_grep'),'name':'By grep'},
                                                       {'loc': url_for('v_grep', q=q, c='1' if caseSensitive else '0'), 'name': q, 'current':1}],
                                        viewernotes=fortunes.short_fortune())

@app.route('/v/grep/<q>/<ident>/<meat>')
def v_grep_viewer(q=None,ident=None,meat=None):
  if (ident == None) != (meat == None):
    return abort(404)
  if not(ident == None) and not(meat == None):
    item = dbops.get_record_by_id(ident)
    if(item == None):
      return abort(404)
    if not(item['Buc_name'] == meat):
      return abort(404)
    return render_article(item, [{'loc': url_for('v_grep'),'name':'By grep'},
                                 {'loc': url_for('v_grep', q=q), 'name': q},
                                 {'loc': url_for('v_grep', q=q, ident=item.doc_id, meat=item['Buc_name']), 'name':meat, 'current':1}])

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
