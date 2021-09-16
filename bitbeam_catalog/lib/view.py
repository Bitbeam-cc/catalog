"""Response generate module."""
from importlib.resources import files
from os.path import join

from jinja2 import Environment, FileSystemLoader

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
