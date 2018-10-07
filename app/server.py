from flask import Flask, redirect, url_for, abort, render_template, make_response, request
app = Flask(__name__)

import sys

from pathlib import Path

import calendar
import magic
from datetime import datetime

import dbops

# Render a specific article from its database entry, given the set of breadcrumbs you want to display.
def render_article(item, breadcrumbs):
  rawname = "/r/" + str(item.doc_id) + "/" + item['Buc_name']

  tags = []
  for tag in item['Buc_tags']:
    tags.append({'name': tag, 'loc': "/v/tag/" + tag})
  timestamp = str(item['ts_year'])+str('/')+str(item['ts_month']) + str('/') + str(item['ts_day']) + ' @ ' + str(item["ts_hour"]) + ":" + str(item['ts_minute']) + ":" + str(item['ts_second'])
  source = url_for('r_file', ident=str(item.doc_id), meat='src', src=item['Buc_source']) if 'Buc_source' in item else None

  return render_template('article.html', article_name=item['Buc_name'], article_timestamp=timestamp, article_title=item['Buc_title'],
                         article_raw=rawname, article_src=source, article_author=item['Buc_author'], article_id=item.doc_id, tags=tags,
                         breadcrumbs=breadcrumbs)

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
  with open(filename, 'rb') as f:
    data = f.read()

  resp = make_response(data)
  # Fudge the mimetypes
  mime = magic.Magic(mime=True).from_file(str(filename))
  print(mime)
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  return resp

# Index endpoint.
@app.route('/')
def index():
  return render_template("index.html", timestamp=datetime.now().strftime("Clock: %A %d %B - %Y/%m/%d %H:%M:%S:%f"))

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
    for year in years:
      items.append({'loc': url_for('v_time', year=str(year)), 'name': year})
    return render_template('viewer.html',items=items,view_name='year', breadcrumbs=[{'loc':url_for('v_time'),'name':'By date', 'current':1}])

  if(month == None):
    months = dbops.get_records_by_date(year)
    for month in months:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month)),'name':calendar.month_name[int(month)]})
    return render_template('viewer.html',items=items,view_name='month',
                           breadcrumbs=[{'loc':url_for('v_time'), 'name': 'By date'},
                                        {'loc':url_for('v_time', year=str(year)),'name': year, 'current':1}])

  if(day == None):
    days = dbops.get_records_by_date(year, month)
    for day in days:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': day})
    return render_template('viewer.html',items=items,view_name='day',
                           breadcrumbs=[{'loc': url_for('v_time'), 'name': 'By date'},
                                        {'loc': url_for('v_time', year=str(year)), 'name': year},
                                        {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)], 'current':1}])

  if(meat == None):
    docs = dbops.get_records_by_date(year, month, day)
    for doc in docs:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month), day=str(day), meat=doc['Buc_name']),
                    'name': doc['Buc_name'] + " (at " + str(doc["ts_hour"]) + ":" + str(doc['ts_minute']) + ":" + str(doc['ts_second']) + ") [tags: " + str(doc['Buc_tags']) + "]"})
    return render_template('viewer.html',items=items,view_name='article',
                           breadcrumbs=[{'loc': url_for('v_time'), 'name': 'By date'},
                                        {'loc': url_for('v_time', year=str(year)), 'name': year},
                                        {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)]},
                                        {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': str(day), 'current':1}])

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
  print(url_for('v_raw', ident = request.form['ident']))
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

  return render_template("v_raw.html")

@app.route('/v/tag/')
@app.route('/v/tag/<path:tags>')
@app.route('/v/tag/<path:tags>/<ident>/<meat>')
def v_tag(tags=None, ident=None, meat=None):
  items = []
  if(tags == None):
    tags = dbops.get_records_by_tag()
    for tag in tags:
      items.append({'loc': url_for('v_tag', tags=tag), 'name': tag})
    return render_template('viewer.html',items=items, view_name='tag', breadcrumbs=[{'loc':url_for('v_tag'),'name':'By tag', 'current':1}])

  tags = tags.split('/')
  nice_tag_list = ""
  if len(tags) == 1:
    nice_tag_list = tags[0]
  else:
    for tag in tags[:-1]:
      nice_tag_list = nice_tag_list + tag + ", "
    nice_tag_list = nice_tag_list + " and " + tags[-1]

  if (ident == None):
    docs = dbops.get_records_by_tag(tags)
    for doc in docs:
      items.append({'loc': url_for('v_tag', tags="/".join(tags), ident=doc.doc_id, meat=doc['Buc_name']),
                    'name': doc['Buc_name'] + " (at " + str(doc["ts_hour"]) + ":" + str(doc['ts_minute']) + ":" + str(doc['ts_second']) + ") [tags: " + str(doc['Buc_tags']) + "]"})
    return render_template('viewer.html', items=items, view_name='tag',
                           breadcrumbs=[{'loc':url_for('v_tag'),'name':'By tag'},
                                        {'loc':url_for('v_tag', tags="/".join(tags)), 'name': nice_tag_list, 'current':1}],
                           viewernotes="<p>Did you know: you can view multiple tags at once by appending them to the URL. For example: <code>/v/tag/tag1/tag2</code>.</p>")

  item = dbops.get_record_by_id(ident)
  if(item == None):
    return abort(404)
  if not(item['Buc_name'] == meat):
    return abort(404)

  return render_article(item, [{'loc': url_for('v_tag'),'name':'By tag'},
                               {'loc': url_for('v_tag', tags="/".join(tags)), 'name': nice_tag_list},
                               {'loc': url_for('v_tag', tags="/".join(tags), ident=item.doc_id, meat=item['Buc_name']), 'name':meat, 'current':1}])
  return abort(501)
