from flask import Flask, redirect, url_for, abort, render_template, make_response
app = Flask(__name__)

from pathlib import Path
from tinydb import TinyDB, Query, where

import calendar
import magic

datadir = Path("../db/data")
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

  if(year == None):
    years = []
    for item in db.table('files'):
      if not(item['ts_year'] in years):
        years.append({'loc':'/v/time/'+str(item['ts_year']),'name':item['ts_year']})
    years.sort()
    return render_template('viewer.html',items=years,view_name='year', breadcrumbs=[{'loc':'/v/time/','name':'By date',  'current':1}])

  if(month == None):
    months = []
    for item in db.table('files').search(where('ts_year')==int(year)):
      if not(item['ts_month'] in months):
        months.append({'loc':'/v/time/'+str(item['ts_year'])+str('/')+str(item['ts_month']),'name':calendar.month_name[item['ts_month']]})
    months.sort()
    return render_template('viewer.html',items=months,view_name='month',
                           breadcrumbs=[{'loc':'/v/time/','name':'By date'},
                                        {'loc':'/v/time/'+str(item['ts_year']),'name':item['ts_year'], 'current':1}])

  if(day == None):
    days = []
    for item in db.table('files').search((where('ts_year')==int(year)) & (where('ts_month')==int(month))):
      if not(item['ts_day'] in days):
        days.append({'loc':'/v/time/'+str(item['ts_year'])+str('/')+str(item['ts_month']) + str('/') + str(item['ts_day']),
                       'name':item['ts_day']})
    days.sort()
    return render_template('viewer.html',items=days,view_name='day',
                           breadcrumbs=[{'loc':'/v/time/','name':'By date'},
                                        {'loc':'/v/time/'+str(item['ts_year']),'name':item['ts_year']},
                                        {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']), 'name': calendar.month_name[item['ts_month']], 'current':1}])

  if(meat == None):
    docs = []
    for item in db.table('files').search((where('ts_year')==int(year)) & (where('ts_month')==int(month)) & (where('ts_day')==int(day))):
      docs.append({'loc':'/v/time/'+str(item['ts_year'])+str('/')+str(item['ts_month']) + str('/') + str(item['ts_day']) + str('/') + item['Buc_name'],
                   'name':item['Buc_name'] + " (at " + str(item["ts_hour"]) + ":" + str(item['ts_minute']) + ":" + str(item['ts_second']) + ") [tags: " + str(item['Buc_tags'].split(',')) + "]"})
    return render_template('viewer.html',items=docs,view_name='article',
                           breadcrumbs=[{'loc':'/v/time/','name':'By date'},
                                        {'loc':'/v/time/'+str(item['ts_year']),'name':item['ts_year']},
                                        {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']), 'name': calendar.month_name[item['ts_month']]},
                                        {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']) + '/' + str(item['ts_day']),
                                         'name':item['ts_day'], 'current':1}])

  item = db.table('files').get((where('ts_year')==int(year)) & (where('ts_month')==int(month)) & (where('ts_day')==int(day)) & (where('Buc_name') == meat))
  print(meat)
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
                         breadcrumbs=[{'loc':'/v/time/','name':'By date'},
                                      {'loc':'/v/time/'+str(item['ts_year']),'name':item['ts_year']},
                                      {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']), 'name': calendar.month_name[item['ts_month']]},
                                      {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']) + '/' + str(item['ts_day']), 'name':item['ts_day']},
                                      {'loc':'/v/time/'+str(item['ts_year'])+'/'+str(item['ts_month']) + '/' + str(item['ts_day']) + '/' + meat, 'name':meat, 'current':1}])

@app.route('/r/')
@app.route('/r/<ident>/')
@app.route('/r/<ident>/<meat>')
def r_file(ident=None,meat=None):
  if (ident == None) | (meat == None):
    return redirect(url_for('index'))

  db = TinyDB(datadir/dbname)
  item = db.table('files').get(doc_id=int(ident))
  print(item)
  if item == None:
    return abort(404)
  if not(item['Buc_name'] == meat):
    return abort(404)

  filename = datadir/str(item['ts_year'])/str(item['ts_month'])/str(item['ts_day'])/str(item['Buc_name'])
  with open(filename) as f:
    data = f.read()

  resp = make_response(data)
  # Fudge the mimetypes
  mime = magic.Magic(mime=True).from_file(str(filename))
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  print(resp)
  return resp
