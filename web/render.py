""" This module contains the web rendering functions for bucephawiki. """

# Standard library
from datetime import datetime, timezone
from pathlib import PurePosixPath, Path
import tempfile
from urllib.parse import unquote

# Libraries
import markdown2
import pypandoc
from flask import Flask, redirect, url_for, abort, render_template, make_response
import frontmatter

# Bucephalus impots
import dbops
from exceptions import *
import fortunes
import tasklist

def breadcrumbs_from_path(path):
  breadcrumbs = [{'loc':url_for('v_page'),'name':'By directory'}]
  nice_path = PurePosixPath(path) # Make it so we can do pathy things.
  for part in nice_path.parts:
    last = breadcrumbs[-1]['loc']
    breadcrumbs.append({'loc': last + '/' + part, 'name': part})
  breadcrumbs[-1]['current'] = 1

  return breadcrumbs

def human_readable_tags(tags):
  tags = ['\"{0}\"'.format(tag) for tag in tags]
  nice_tag_list = ""
  if len(tags) == 1:
    nice_tag_list = tags[0]
  elif len(tags) > 1:
    for tag in tags[:-1]:
      nice_tag_list = nice_tag_list + tag + ", "
    nice_tag_list = nice_tag_list + " and " + tags[-1]
  return nice_tag_list

def render_directory(path):
  if dbops.path_type(path) != dbops.PathType.DIRECTORY:
    raise FileNotDirectoryError(path)

  items = []
  pages = dbops.directory_contents(path)
  for page in pages:
    items.append({'loc': url_for('v_page', path = path + "/"+str(page)), 'name': str(page)})

  breadcrumbs=breadcrumbs_from_path(path)

  return render_template('viewer.html',items=items,view_name='directory', breadcrumbs=breadcrumbs, viewernotes=fortunes.short_fortune())


def render_wiki(path):
  if dbops.path_type(path) != dbops.PathType.TEXT:
    raise WrongPathTypeError(path)

  print(unquote(url_for('v_page',path=r'\1')))
  text = markdown2.markdown(dbops.read_path_content(path),
                            extras=["link-patterns", "fenced-code-blocks"],
                            link_patterns=[(dbops.valid_path_re, unquote(url_for('v_page',path=r'\1')))])


  breadcrumbs = breadcrumbs_from_path(path)

  metadata = dbops.read_path_metadata(path)

  return render_template('article.html',
                         article_name=PurePosixPath(path).name,
                         article_timestamp=metadata['timestamp_create'],
                         article_author=metadata['author'],
                         tags=human_readable_tags(metadata['tags']),
                         breadcrumbs=breadcrumbs,
                         article_modded=metadata['timestamp_modify'],
                         article_edit=url_for('v_page',path=path,edit=1),
                         article_pdf=url_for('v_page',path=path,pdf=1),
                         viewernotes=fortunes.short_fortune(),
                         html_text=text)

def render_edit(path, isnew):
  if not isnew and dbops.path_type(path) != dbops.PathType.TEXT:
    raise WrongPathTypeError(path)

  if isnew:
    text = "# " + path
  else:
    text = dbops.read_path_content(path)

  breadcrumbs = breadcrumbs_from_path(path)
  breadcrumbs[-1].pop('current',None)
  breadcrumbs.append({'loc': url_for('v_page', path=path, edit=1), 'name': '(edit)', 'current': 1})

  # TODO: load from defaults.json like we used to.
  if isnew:
    metadata = {'path': path, 'timestamp_create': '"to be set upon commit"', 'author':'', 'tags': []}
  else:
    metadata = dbops.read_path_metadata(path)

  mdtext = frontmatter.dumps(frontmatter.Post(text,**metadata))

  return render_template('editor.html',
                         article_name=PurePosixPath(path).name,
                         article_timestamp=metadata['timestamp_create'],
                         article_author=metadata['author'],
                         tags=human_readable_tags(metadata['tags']),
                         breadcrumbs=breadcrumbs,
                         abort_url=url_for('v_page',path=path),
                         post_url=url_for('v_page',path=path),
                         viewernotes=fortunes.short_fortune(),
                         html_text=mdtext)

def write_wiki(path, yamltext):
  if dbops.path_exists(path) and dbops.path_type(path) != dbops.PathType.TEXT:
    raise WrongPathTypeError(path)

  post = frontmatter.loads(yamltext)
  metadata = post.metadata
  text = post.content

  dbops.write_path_text(path, text, metadata)

def render_pdf(path):
  if dbops.path_type(path) != dbops.PathType.TEXT:
    raise WrongPathTypeError(path)

  filename = tempfile.mkstemp('.pdf')[1]
  try:
    pypandoc.convert_text("# " + path + "\nRetrieved " + datetime.now(timezone.utc).strftime("%d %B %Y (%Z) @ %H:%M:%S")
                              + "\n\n---\n" + dbops.read_path_content(path), 'pdf', format='md', outputfile=filename)
    with open(filename, 'rb') as f:
      data = f.read()

    resp = make_response(data)
    resp.headers['Content-Type'] = 'application/pdf'
  finally:
    Path(filename).unlink()

  return resp

def render_raw(path):
  if dbops.path_type(path) != dbops.PathType.TEXT or dbops.path_type(path) != dbops.PathType.BLOB:
    raise WrongPathTypeError(path)


  resp = make_response(dbops.read_path_content(path))

  # Fudge the mimetypes
  mime = magic.Magic(mime=True).from_file(str(filename))
  if ("text/" in mime) & (not("html" in mime)):
    resp.headers['Content-Type'] = 'text/plain'
  else:
    resp.headers['Content-Type'] = mime
  return resp

def render_geogebra(path):
  if dbops.path_type(path) != dbops.PathType.TEXT:
    raise WrongPathTypeError(path)

  text = markdown2.markdown(dbops.read_path_content(path),
                            extras=["link-patterns", "fenced-code-blocks"],
                            link_patterns=[(valid_path_re, url_for('v_page',path='\\1'))])


  breadcrumbs = breadcrumbs_from_path(path)

  metadata = dbops.read_path_metadata(path)

  return render_template('ggbframe.html',
                         article_name=PurePosixPath(path).name,
                         article_timestamp=metadata['timestamp_create'],
                         article_author=metadata['author'],
                         tags=human_readable_tags(metadata['tags']),
                         breadcrumbs=breadcrumbs,
                         article_modded=metadata['timestamp_modify'],
                         viewernotes=fortunes.short_fortune(),
                         ggbfilename=url_for('v_page',path=path,raw=1))
