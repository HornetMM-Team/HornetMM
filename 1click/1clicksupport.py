import urllib.parse

def parse_gamebanana_link(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme == "gamebanana" and parsed_url.netloc == "install":
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == "mod":
            mod_id = path_parts[2]
            return mod_id
    return None


