import os
from six.moves.urllib.parse  import urlparse,unquote

from offline_docs.settings import DOCS_STORE


def create_path(url):
    u = urlparse(url)
    f = unquote(u.path)
    p = DOCS_STORE+os.path.dirname(f)
    if not os.path.isdir(p):
        try:
            os.makedirs(p,0o755)
        except OSError as e:
            print(e)
    return os.path.join(p,os.path.basename(f))


