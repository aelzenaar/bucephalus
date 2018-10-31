from flask import Flask, redirect, url_for, abort, render_template, make_response, request, escape
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from werkzeug import unescape
app = Flask(__name__)

import sys

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

def get_fortune():
  now = datetime.now()
  if(now.month == 3 and now.day == 14):
    return "<a href=\"https://www.youtube.com/watch?v=FtxmFlMLYRI\">happy $\pi$ day</a>."
  if(now.month == 4 and now.day == 26):
    return "<a href=\"https://www.youtube.com/watch?v=PWZYId1fWnM\">it's April 26</a>."
  did_you_know = ["you can view multiple tags at once by appending them to the URL. For example: <code>/v/tag/tag1/tag2</code>.",
                  "the search functionality doesn't actually work.",
                  "the search functionality allows regular expressions.",
                  "eventually, Bucephalus will integrate with git.",
                  "eventually, Bucephalus will integrate with geogebra.",
                  "eventually, Bucephalus will have more features.",
                  "Bucephalus is running on Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + ".",
                  "you can update files using the command line after adding them.",
                  "if your files are lost, you'll wish you had a backup.",
                  "'Βουκέφαλος' means ox-head.",
                  "Bucephalus was named after a mark on his body depicting the head of an ox.",
                  "the pigeonhole principle will probably solve your problem.",
                  "$3987^{12} + 4365^{12} = 4472^{12}$",
                  "oops.",
                  "in science one tries to tell people, in such a way as to be understood by everyone, something that no one ever knew before. But in poetry, it's the exact opposite. (PAM Dirac)"
                  ]

  return "Did you know: " + random.choice(did_you_know)

def get_randomse():
  if not config.enable_long_fortunes():
    return None
  try:
    questionid = random.choice([{'qid':22299, 'site':"mathoverflow.net"}, {'qid':1083, 'site':"mathoverflow.net"},
                                {'qid':7155, 'site':"mathoverflow.net"}, {'qid':2144, 'site':"mathoverflow.net"},
                                {'qid':14574, 'site':"mathoverflow.net"}, {'qid':879, 'site':"mathoverflow.net"},
                                {'qid':16829, 'site':"mathoverflow.net"}, {'qid':47214, 'site':"mathoverflow.net"},
                                {'qid':44326, 'site':"mathoverflow.net"}, {'qid':29006, 'site':"mathoverflow.net"},
                                {'qid':38856, 'site':"mathoverflow.net"}, {'qid':7584, 'site':"mathoverflow.net"},
                                {'qid':117668, 'site':"mathoverflow.net"}, {'qid':8846, 'site':"mathoverflow.net"},
                                {'qid':178139, 'site':"mathoverflow.net"}, {'qid':42512, 'site':"mathoverflow.net"},
                                {'qid':4994, 'site':"mathoverflow.net"},
                                {'qid':733754, 'site':"math.stackexchange.com"}, {'qid':323334, 'site':"math.stackexchange.com"},
                                {'qid':178940, 'site':"math.stackexchange.com"}, {'qid':111440, 'site':"math.stackexchange.com"},
                                {'qid':250, 'site':"math.stackexchange.com"}, {'qid':820686, 'site':"math.stackexchange.com"},
                                {'qid':505367, 'site':"math.stackexchange.com"}, {'qid':362446, 'site':"math.stackexchange.com"},
                                {'qid':8814, 'site':"math.stackexchange.com"}, {'qid':260656, 'site':"math.stackexchange.com"},
                                {'qid':2949, 'site':"math.stackexchange.com"},
                                {'qid':4351, 'site':"matheducators.stackexchange.com"}, {'qid':1817, 'site':"matheducators.stackexchange.com"},
                              ])
    question = requests.get('https://api.stackexchange.com/questions/' + str(questionid['qid']) + '?site=' + str(questionid['site']) +
                            '&filter=!gB66oJbwvcXSH(Ni5Ti9FQ4PaxMw.WKlBWC')
    question.raise_for_status()
    question = question.json()['items'][0]
    ansid = random.choice(question['answers'])['answer_id']

    fullrequest = requests.get('https://api.stackexchange.com/answers/' + str(ansid) + '?site=' + str(questionid['site']) +
                              '&filter=!Fcb(61J.xH8s_mAfP-LmG*7fPe')
    fullrequest.raise_for_status()
    fullrequest = fullrequest.json()
    answer = fullrequest['items'][0]

    randomse = {'qtitle': unescape(question['title']), 'qbody': question['body'], 'qlink': question['link'],
                'abody': answer['body'], 'alink': answer['link'], 'ascore': answer['score'], 'quota': fullrequest['quota_remaining'] }
    return randomse
  except Exception as ex:
    randomse = {'qtitle': 'Exception occurred', 'qbody': str(ex), 'qlink': 'https://xkcd.com/1084/',
                'abody': '<img src="https://imgs.xkcd.com/comics/error_code.png"/>', 'alink': 'https://xkcd.com/1024/', 'ascore': '', 'quota': '' }
    return randomse

def timestamp_for_item(item):
  timestamp = str(item['ts_year']) + str('/') + str(item['ts_month']) + str('/') + str(item['ts_day']) + ' @ ' +\
              str(item["ts_hour"]).zfill(2) + ":" + str(item['ts_minute']).zfill(2) + ":" + str(item['ts_second']).zfill(2)

  if('ts_year2' in item):
    modified  = str(item['ts_year2']) + str('/') + str(item['ts_month2']) + str('/') + str(item['ts_day2']) + ' @ ' +\
                str(item["ts_hour2"]).zfill(2) + ":" + str(item['ts_minute2']).zfill(2) + ":" + str(item['ts_second2']).zfill(2)
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
  rawname = "/r/" + str(item.doc_id) + "/" + item['Buc_name']

  tags = []
  for tag in item['Buc_tags']:
    tags.append({'name': str(escape(tag)).replace(' ', '&nbsp;'), 'loc': "/v/tag/" + tag})
  timestamp, modified = timestamp_for_item(item)
  source = url_for('r_file', ident=str(item.doc_id), meat='src', src=item['Buc_source']) if 'Buc_source' in item else None

  return render_template('article.html', article_name=item['Buc_name'], article_timestamp=timestamp, article_title=item['Buc_title'],
                         article_raw=rawname, article_src=source, article_author=item['Buc_author'], article_id=item.doc_id, tags=tags,
                         breadcrumbs=breadcrumbs, article_modded=modified, viewernotes=get_fortune())

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
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  return resp

# Index endpoint.
@app.route('/')
def index():
  return render_template("index.html", timestamp=datetime.now().strftime("Clock: %A %d %B - %Y/%m/%d %H:%M:%S:%f"), randomse=get_randomse(), viewernotes=get_fortune())

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
    return render_template('viewer.html',items=items,view_name='year', breadcrumbs=[{'loc':url_for('v_time'),'name':'By date', 'current':1}], viewernotes=get_fortune())

  if(month == None):
    months = dbops.get_records_by_date(year)
    if not months:
      abort(404)
    for month in months:
      items.append({'loc': url_for('v_time', year=str(year), month=str(month)),'name':calendar.month_name[int(month)]})
    return render_template('viewer.html',items=items,view_name='month',
                           breadcrumbs=[{'loc':url_for('v_time'), 'name': 'By date'},
                                        {'loc':url_for('v_time', year=str(year)),'name': year, 'current':1}], viewernotes=get_fortune())

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
                           viewernotes=get_fortune())

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
                           viewernotes=get_fortune())

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
                         viewernotes=get_fortune())

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
                           viewernotes=get_fortune())

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
                           viewernotes=get_fortune())

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
                          viewernotes=get_fortune())

  return abort(501)

# Endpoint to handle search-by-content. Redirects back to the main endpoint.
@app.route('/v/grep/post', methods=['POST'])
def v_grep_post():
  if(request.form['q'] == ''):
    return redirect(url_for('v_grep', q = '#'))

  return redirect(url_for('v_grep', q = request.form['q'], c=request.form.get('checkCase', '1')))

# Main endpoint for search-by-ID
@app.route('/v/grep/')
@app.route('/v/grep/<q>/')
@app.route('/v/grep/<q>/<ident>/<meat>')
def v_grep(q=None,ident=None,meat=None):
  if q == None:
    return render_template("v_grep.html", searchtype="initial", viewernotes=get_fortune())
  if q == '#':
    return render_template("v_grep.html", searchtype="noquery", viewernotes=get_fortune())

  # One of ident and meat was provided but not the other
  if (ident == None) != (meat == None):
    return abort(404)

  # Query, ident, and meat provided.
  if not(ident == None) and not(meat == None):
    item = dbops.get_record_by_id(ident)
    if(item == None):
      return abort(404)
    if not(item['Buc_name'] == meat):
      return abort(404)
    return render_article(item, [{'loc': url_for('v_grep'),'name':'By grep'},
                                {'loc': url_for('v_grep', q=q), 'name': q},
                                {'loc': url_for('v_grep', q=q, ident=item.doc_id, meat=item['Buc_name']), 'name':meat, 'current':1}])

  # So we have a query to search.
  case = False if request.args.get("c", '1') == '0' else True
  files = search.search_files_for_string(q, case)
  if(files == []):
    return render_template("v_grep.html", searchtype="empty", q=q, viewernotes=get_fortune())

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
      items.append({'loc': url_for('v_grep', q=q, ident=item.doc_id, meat=item['Buc_name']),
                    'name': menu_name_for_item(item)})
  if (items == []):
    return render_template("v_grep.html", searchtype="empty", q=q, viewernotes=get_fortune())

  return render_template('viewer.html', items=items, view_name='grep', breadcrumbs = [{'loc': url_for('v_grep'),'name':'By grep'},
                                                                                     {'loc': url_for('v_grep', q=q), 'name': q, 'current':1}],
                                                                       viewernotes=get_fortune())

@app.route('/v/tasks', methods=['POST', 'GET'])
def v_tasks():
  if(request.method == 'POST'):
    print("in post")
    if 'add' in request.form:
      tasklist.add(request.form['toadd'])
    elif 'todelete' in request.form:
      print(request.form.getlist('delete'))
      tasklist.rm(request.form.getlist('delete'))

  return render_template('tasklist.html', tasks=tasklist.tasks(), breadcrumbs = [{'loc': url_for('v_tasks'),'name':'Task list','current':1}],
                         viewernotes=get_fortune())

@app.route('/v/coffee')
def brew_coffee():
  abort(418)

#@app.errorhandler(Exception)
def handle_error(e):
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
