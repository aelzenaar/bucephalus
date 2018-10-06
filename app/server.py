from flask import Flask, redirect, url_for, abort, render_template, make_response
app = Flask(__name__)

import sys

from pathlib import Path
from tinydb import TinyDB, Query, where

import calendar
import magic

import dbops

datadir = Path("./data")
dbname = "database.db"

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/v/')
def noview():
  return redirect(url_for('index'))

@app.route('/v/time/')
@app.route('/v/time/<year>/')
@app.route('/v/time/<year>/<month>/')
@app.route('/v/time/<year>/<month>/<day>/')
@app.route('/v/time/<year>/<month>/<day>/<meat>/')
def v_time(year=None,month=None,day=None,meat=None):
  db = TinyDB(datadir/dbname)

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

  rawname = "/r/" + str(item.doc_id) + "/" + meat

  tags = []
  for tag in item['Buc_tags']:
    tags.append({'name': tag, 'loc': "/v/tag/" + tag})
  timestamp = str(item['ts_year'])+str('/')+str(item['ts_month']) + str('/') + str(item['ts_day']) + ' @ ' + str(item["ts_hour"]) + ":" + str(item['ts_minute']) + ":" + str(item['ts_second'])
  source = item['Buc_source'] if 'Buc_source' in item else None

  return render_template('article.html', article_name=item['Buc_name'], article_timestamp=timestamp, article_title=item['Buc_title'],
                         article_raw=rawname, article_src=source,
                         breadcrumbs=[{'loc': url_for('v_time'), 'name': 'By date'},
                                      {'loc': url_for('v_time', year=str(year)), 'name': year},
                                      {'loc': url_for('v_time', year=str(year), month=str(month)), 'name': calendar.month_name[int(month)]},
                                      {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day)), 'name': str(day)},
                                      {'loc': url_for('v_time', year=str(year), month=str(month), day=str(day), meat=meat), 'name':meat, 'current':1}])

@app.route('/r/')
@app.route('/r/<ident>/')
@app.route('/r/<ident>/<meat>')
def r_file(ident=None,meat=None):
  if (ident == None) | (meat == None):
    return redirect(url_for('index'))

  db = TinyDB(datadir/dbname)
  item = db.table('files').get(doc_id=int(ident))
  if item == None:
    return abort(404)
  if not(item['Buc_name'] == meat):
    return abort(404)

  filename = datadir/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/str(item['Buc_name'])
  with open(filename, 'rb') as f:
    data = f.read()

  resp = make_response(data)
  # Fudge the mimetypes
  mime = magic.Magic(mime=True).from_file(str(filename))
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  return resp
