from pathlib import Path

# Directory for user-specific data (e.g. the database)
def get_user_data_dir():
  return Path.home()/"bucephalus"

# Directory for library files, prototypes for horsepee, and so forth
def get_install_dir():
  return Path(__file__).parent.parent

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
