from pathlib import Path

def get_user_data_dir():
  return Path.home()/"bucephalus"

def get_install_dir():
  return Path(__file__).parent
