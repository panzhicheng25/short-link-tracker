import re

BROWSERS = [
    ('Edge', r'Edg/(\d+)'), ('Chrome', r'Chrome/(\d+)'),
    ('Firefox', r'Firefox/(\d+)'), ('Safari', r'Safari/(\d+)'), ('Opera', r'OPR/(\d+)'),
]
OS_MAP = [
    ('Android', r'Android'), ('iOS', r'(iPhone|iPad|iPod)'),
    ('Windows', r'Windows'), ('macOS', r'Macintosh'), ('Linux', r'Linux'),
]

def parse(ua_string):
    if not ua_string:
        return {'browser': '', 'os': '', 'device': 'Desktop'}
    browser = 'Other'
    for name, pattern in BROWSERS:
        if re.search(pattern, ua_string):
            browser = name
            break
    os_name = 'Other'
    for name, pattern in OS_MAP:
        if re.search(pattern, ua_string):
            os_name = name
            break
    if 'Mobile' in ua_string or 'Android' in ua_string or 'iPhone' in ua_string:
        device = 'Mobile'
    elif 'iPad' in ua_string or 'Tablet' in ua_string:
        device = 'Tablet'
    else:
        device = 'Desktop'
    return {'browser': browser, 'os': os_name, 'device': device}
