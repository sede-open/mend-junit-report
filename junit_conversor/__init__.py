import xml.etree.cElementTree as ET
import sys
from collections import defaultdict
import json


def _parse(input):
    with open(input, 'r') as f:
        json_content = json.load(f)

    libraries = json_content['libraries']

    parsed = defaultdict(list)

    for library in libraries:

        try:
            vulnerabilities = library['vulnerabilities']
        except KeyError:
            Warning("You input file contains invalid lines")
            vulnerabilities = {}

        # Skip invalid lines
        if len(vulnerabilities) != 0:

            library_name = library['name']

            for vulnerability in vulnerabilities:

                error = {
                    'name': "{0}:{1}".format(library_name, vulnerability['name']),
                    'file': library_name,
                    'code': vulnerability['type'],
                    'severity': vulnerability['severity'],
                    'score': vulnerability['score'],
                    'detail': vulnerability['description']
                }

                parsed[error['name']].append(error)

    return dict(parsed)


def _convert(origin, destination):
    parsed = _parse(origin)

    testsuite = ET.Element("testsuite")
    testsuite.attrib["errors"] = str(len(parsed))
    testsuite.attrib["failures"] = "0"
    testsuite.attrib["name"] = "Whitesource"
    testsuite.attrib["tests"] = str(len(parsed)) or "1"
    testsuite.attrib["time"] = "1"

    for file_name, errors in parsed.items():
        testcase = ET.SubElement(testsuite, "testcase", name=file_name, class_name=file_name.split(":", 2)[0])

        for error in errors:
            kargs = {
                "file": error['file'],
                "line": "",
                "col": "",
                "message": "{0}: {1}".format(error['file'], error['detail']),
                "type": "Whitesource %s" % error['code']
            }

            text = "{0}:{1}:{2} {3}:{4}".format(error['code'], error['severity'], error['score'], error['file'], error['detail'])

            ET.SubElement(testcase, "failure", **kargs).text = text

    tree = ET.ElementTree(testsuite)

    if (2, 6) == sys.version_info[:2]:  # py26
        tree.write(destination, encoding='utf-8')
    else:
        tree.write(destination, encoding='utf-8', xml_declaration=True)
