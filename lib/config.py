from pathlib import Path

# Directory for user-specific data (e.g. the database)
def get_user_data_dir():
  return Path.home()/"bucephalus2"

# Directory for library files, default stencils for bucvac, and so forth
def get_install_dir():
  return Path(__file__).parent.parent

# Directory where the actual user-given files are kept.
def get_wiki_dir():
  return get_user_data_dir()/"files"

# File holding metadata on our pages.
def get_metadata_file_path():
  return get_user_data_dir()/"metadata.json"

# File holding default keys used by bucadd and bucvac; edited by bucdef
def get_defaults_file_path():
  return get_user_data_dir()/"defaults.json"

# File holding recently added/modified articles
def get_recent_file_path():
  return get_user_data_dir()/"recent.json"

# File holding details of article pinned to front page
def get_pinned_file_path():
  return get_user_data_dir()/"pinned.json"

# Search paths for bucvac stencils, in search order.
def get_stencils_search_dirs():
  return [get_user_data_dir()/"stencils", get_install_dir()/"stencils"]

# Enable the long-form random content on the homepage.
def enable_long_fortunes():
  return True

# Enable tasklist read access from the web
def enable_tasklist_web():
  return True

# Enable tasklist write access from the web
def enable_tasklist_web_write():
  if not enable_tasklist_web():
    return False

  return True

# Enable Geogebra integration on the web
def enable_ggb_integration():
  return True

# Enable VCS commits on all database changes
def enable_vcs_commits():
  return True

# Timeout (in seconds) for web requests
def external_request_timeout():
  return 1
