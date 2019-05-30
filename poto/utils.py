import os

def set_home(path):
    home = os.path.expanduser('~')
    if home not in path:
        if '~' in path:
            path = re.sub('~', home, path)
        else:
            path = os.path.join(home, path)
    
    return path