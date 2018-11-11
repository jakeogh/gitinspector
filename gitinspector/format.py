# coding: utf-8
#
# Copyright © 2012-2015 Ejwa Software. All rights reserved.
#
# This file is part of gitinspector.
#
# gitinspector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gitinspector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gitinspector. If not, see <http://www.gnu.org/licenses/>.

import base64
import os
import textwrap
import time
import zipfile
from . import basedir, localization, terminal, version

__available_formats__ = ["html", "htmlembedded", "json", "text", "xml"]

DEFAULT_FORMAT = __available_formats__[3]

__selected_format__ = DEFAULT_FORMAT

class InvalidFormatError(Exception):
    def __init__(self, msg):
        super(InvalidFormatError, self).__init__(msg)
        self.msg = msg

def select(format):
    global __selected_format__
    __selected_format__ = format

    return format in __available_formats__

def get_selected():
    return __selected_format__

def is_interactive_format():
    return __selected_format__ == "text"

def __output_html_template__(name):
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
    file_r = open(template_path, "rb")
    template = file_r.read().decode("utf-8", "replace")

    file_r.close()
    return template

def __get_zip_file_content__(name, file_name="/html/flot.zip"):
    zip_file = zipfile.ZipFile(basedir.get_basedir() + file_name, "r")
    content = zip_file.read(name)

    zip_file.close()
    return content.decode("utf-8", "replace")

INFO_ONE_REPOSITORY = lambda: _("Statistical information for the repository '{0}' was gathered on {1}.")
INFO_MANY_REPOSITORIES = lambda: _("Statistical information for the repositories '{0}' was gathered on {1}.")

def output_header(runner):
    """
    The function responsible for outputting a header to the
    output. For the HTML-like outputs, this also means handling the
    different Javascript files that are included or not inside the
    output.
    """
    repos = runner.repos
    repos_string = ", ".join([repo.name for repo in repos])

    if __selected_format__ == "html" or __selected_format__ == "htmlembedded":
        base = basedir.get_basedir()
        html_header = __output_html_template__(base + "/templates/header.html")
        tablesorter_js = __get_zip_file_content__("jquery.tablesorter.min.js",
                                                  "/html/jquery.tablesorter.min.js.zip").encode("latin-1", "replace")
        tablesorter_js = tablesorter_js.decode("utf-8", "ignore")
        flot_js = __get_zip_file_content__("jquery.flot.js")
        pie_js = __get_zip_file_content__("jquery.flot.pie.js")
        resize_js = __get_zip_file_content__("jquery.flot.resize.js")

        logo_file = open(base + "/html/gitinspector_piclet.png", "rb")
        logo = logo_file.read()
        logo_file.close()
        logo = base64.b64encode(logo)

        if __selected_format__ == "htmlembedded":
            jquery_js = "<script type='application/javascript'>" + \
                __output_html_template__(base + "/html/jquery.min.js") + "</script>"
            d3_js = "<script type='application/javascript'>" + \
                __output_html_template__(base + "/html/d3.min.js") + "</script>"
        else:
            jquery_js = ("<script type='application/javascript'"
                         "src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js\">")
            d3_js = ("toto" + "<script type='application/javascript'"
                         "src=\"https://ajax.googleapis.com/ajax/libs/d3js/5.7.0/d3.min.js\">")
        repos_name = (repos_string if runner.config.branch == "master"
                     else "%s (branch %s)"%(repos_string, runner.config.branch))
        repos_text = (INFO_ONE_REPOSITORY() if len(repos) <= 1 else
                      INFO_MANY_REPOSITORIES()).format(repos_name, localization.get_date())
        runner.out.writeln(html_header.format(title=_("Repository statistics for '{0}'").format(repos_string),
                                              jquery=jquery_js,
                                              jquery_tablesorter=tablesorter_js,
                                              jquery_flot=flot_js,
                                              jquery_flot_pie=pie_js,
                                              jquery_flot_resize=resize_js,
                                              d3=d3_js,
                                              logo=logo.decode("utf-8", "replace"),
                                              logo_text=_("The output has been generated by {0} {1}. The statistical analysis tool"
                                                          " for git repositories.").format(
                                                              "<a href=\"https://github.com/ejwa/gitinspector\">gitinspector</a>",
                                                              version.__version__),
                                              repo_text=repos_text,
                                              show_minor_authors=_("Show minor authors"),
                                              hide_minor_authors=_("Hide minor authors"),
                                              show_minor_rows=_("Show rows with minor work"),
                                              hide_minor_rows=_("Hide rows with minor work")))
    elif __selected_format__ == "json":
        runner.out.writeln("{\n\t\"gitinspector\": {")
        runner.out.writeln("\t\t\"version\": \"" + version.__version__ + "\",")

        if len(repos) <= 1:
            runner.out.writeln("\t\t\"repository\": \"" + repos_string + "\",")
        else:
            repos_json = "\t\t\"repositories\": [ "

            for repo in repos:
                repos_json += "\"" + repo.name + "\", "

            runner.out.writeln(repos_json[:-2] + " ],")

        runner.out.writeln("\t\t\"report_date\": \"" + time.strftime("%Y/%m/%d") + "\",")

    elif __selected_format__ == "xml":
        runner.out.writeln("<gitinspector>")
        runner.out.writeln("\t<version>" + version.__version__ + "</version>")

        if len(repos) <= 1:
            runner.out.writeln("\t<repository>" + repos_string + "</repository>")
        else:
            runner.out.writeln("\t<repositories>")

            for repo in repos:
                runner.out.writeln("\t\t<repository>" + repo.name + "</repository>")

            runner.out.writeln("\t</repositories>")

        runner.out.writeln("\t<report-date>" + time.strftime("%Y/%m/%d") + "</report-date>")
    else:
        repos_name = (repos_string if runner.config.branch == "master"
                     else "%s (branch %s)"%(repos_string, runner.config.branch))
        repos_text = (INFO_ONE_REPOSITORY() if len(repos) <= 1 else
                      INFO_MANY_REPOSITORIES()).format(repos_name, localization.get_date())

        runner.out.writeln(textwrap.fill(repos_text, width=terminal.get_size()[0]))

def output_footer(runner):
    """
    The function responsible for outputting a footer to the output.
    """
    if __selected_format__ == "html" or __selected_format__ == "htmlembedded":
        base = basedir.get_basedir()
        html_footer = __output_html_template__(base + "/templates/footer.html")
        runner.out.writeln(html_footer)
    elif __selected_format__ == "json":
        runner.out.writeln("\n\t}\n}")
    elif __selected_format__ == "xml":
        runner.out.writeln("</gitinspector>")
