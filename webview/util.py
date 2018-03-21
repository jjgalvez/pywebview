# -*- coding: utf-8 -*-

"""
(C) 2014-2018 Roman Sirokov and contributors
Licensed under BSD license

http://github.com/r0x0r/pywebview/
"""

import os
import re
import sys

from .js import api


def base_uri(relative_path=''):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return 'file://%s' % os.path.join(base_path, relative_path)


def convert_string(string):
    if sys.version < '3':
        return unicode(string)
    else:
        return str(string)


def parse_file_type(file_type):
    '''
    :param file_type: file type string 'description (*.file_extension1;*.file_extension2)' as required by file filter in create_file_dialog
    :return: (description, file extensions) tuple
    '''
    valid_file_filter = r'^([\w ]+)\((\*(?:\.(?:\w+|\*))*(?:;\*\.\w+)*)\)$'
    match = re.search(valid_file_filter, file_type)

    if match:
        return match.group(1).rstrip(), match.group(2)
    else:
        raise ValueError('{0} is not a valid file filter'.format(file_type))


def parse_api_js(api_instance):
    func_list = [str(f) for f in dir(api_instance) if callable(getattr(api_instance, f)) and str(f)[0] != '_']
    js_code = api.src % func_list

    return js_code


def escape_string(string):
    return string\
        .replace('\\', '\\\\') \
        .replace('"', r'\"') \
        .replace('\n', r'\n')\
        .replace('\r', r'\r')


def transform_url(url):
    if url is None or ':' not in url:
        return url
    else:
        return 'file://' + os.path.abspath(url)


def make_unicode(string):
    """
    Python 2 and 3 compatibility function that converts a string to Unicode. In case of Unicode, the string is returned
    unchanged
    :param string: input string
    :return: Unicode string
    """
    if sys.version < '3' and isinstance(string, str):
        return unicode(string.decode('utf-8'))

    return string


def escape_line_breaks(string):
    return string.replace('\\n', '\\\\n').replace('\\r', '\\\\r')


def inject_base_uri(content):
    _base_uri = base_uri()
    pattern = '<%s(?:[\s]+[^>]*|)>'
    base_tag = '<base href="%s">' % _base_uri

    match = re.search(pattern % 'base', content)

    if match:
        return content

    match = re.search(pattern % 'head', content)
    if match:
        tag = match.group()
        return content.replace(tag, tag + base_tag)

    match = re.search(pattern % 'html', content)
    if match:
        tag = match.group()
        return content.replace(tag, tag + base_tag)

    match = re.search(pattern % 'body', content)
    if match:
        tag = match.group()
        return content.replace(tag, base_tag + tag)

    return base_tag + content


def inject_css(html, css):
    pattern = '<%s(?:[\s]+[^>]*|)>'
    style_tag = '<style type="text/css">%s</style>' % css

    if '</head>' in html:
        return html.replace('</head>', style_tag + '</head>')

    match = re.search(pattern % 'body', content)
    if match:
        tag = match.group()
        return content.replace(tag, tag + style_tag)

    if '</html>' in html:
        return html.replace('</html>', style_tag + '</html>')

    return style_tag + html