import config
import subprocess

def commit(mesg):
  if not config.enable_vcs_commits():
    return

  print('*** Bucephalus VCS is enabled: commit: ' + mesg)
  path = config.get_user_data_dir()
  if not ((path/".git").exists() and (path/".git").is_dir()):
    subprocess.call(['git', '-C', str(path), 'init'])
    commit(mesg)
    return

  subprocess.call(['git', '-C', str(path), 'add', '--quiet', str(path)])
  subprocess.call(['git', '-C', str(path), 'commit', '--quiet', '-m', 'Bucephalus: ' + mesg, '--author=Bucephalus Automated <bucep5@localhost>'])
