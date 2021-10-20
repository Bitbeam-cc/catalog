"""Response generate module."""
from importlib.resources import files
from os.path import join

from docutils.core import publish_parts
from docutils_tinyhtml import Writer
from jinja2 import Environment, FileSystemLoader
from m2r import convert

TEMPL_PATH = (join(str(files('bitbeam_catalog')), 'templates'))


def package_to_api(pkg):
    """Convert pkg_resources.DistInfoDistribution to API."""
    return {
        'name': pkg.project_name,
        'version': pkg.version,
        'path': pkg.module_path
    }


def generate_page(template, **kwargs):
    """Return generated ouptut fromjinja template."""

    env = Environment(loader=FileSystemLoader(TEMPL_PATH),
                      extensions=[
                          'jinja2.ext.i18n', 'jinja2.ext.do',
                          'jinja2.ext.loopcontrols'
                      ])

    tmpl = env.get_template(template)
    return tmpl.render(kwargs)


def markdown2html(source):
    """Return generated html from markdown source."""
    with open(source, encoding="utf-8") as src:
        md_ = src.read()
        rst = convert(md_)
        parts = publish_parts(source=rst,
                              writer=Writer(),
                              writer_name='html',
                              settings_overrides={'no_system_messages': True})
        html = parts['html_title'] + parts['body']
        if parts.get('html_footnotes') or parts.get('html_citations'):
            html = parts.get('html_line', '') + \
                parts.get('html_footnotes', '') + \
                parts.get('html_citations', '')
        return html
