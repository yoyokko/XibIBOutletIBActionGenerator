#/usr/bin/python

__author__ = 'yoyokko@gmail.com'

import sys, getopt
import os
import xml.dom.minidom
import random
from xcodeclass import *

randomcharacters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

class Property:
    def __init__(self):
        self.name = ''
        self.type = ''
        self.identify = ''

    def print_me(self):
        print '<%s id="%s" name="%s">' % (self.type, self.identify, self.name)


def randomidentify():
    return '{0:s}{1:s}{2:s}-{3:s}{4:s}-{5:s}{6:s}{7:s}'.format(
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))],
        randomcharacters[random.randrange(0, len(randomcharacters))])


def parseoneview(xmldocument, viewdom, properties=[], actions=[]):
    identifiy = viewdom.getAttribute('id')
    userlabel = viewdom.getAttribute('userLabel')
    if userlabel == '':
        accessibilitys = viewdom.childNodes
        for accessibility in accessibilitys:
            if accessibility.nodeType == accessibility.ELEMENT_NODE:
                keyname = accessibility.getAttribute('key')
                if keyname == 'accessibilityConfiguration':
                    userlabel = accessibility.getAttribute('label')
                    break

    propertytype = 'UI' + viewdom.tagName.title()

    if propertytype.endswith('view'):
        propertytype = propertytype[:-4] + 'View'

    labelnames = userlabel.split(';')

    if len(labelnames) > 0 and userlabel != '':
        for labelname in labelnames:
            if labelname.startswith('@sel('):
                # this is a isaction
                # try to get connections under current xml node
                sel = labelname[5:-1]
                actions.append(sel)

                connections = viewdom.getElementsByTagName('connections')
                if len(connections) == 0:
                    # create connections element if not exist
                    connections = xmldocument.createElement('connections')
                    viewdom.appendChild(connections)
                    connection = connections
                else:
                    connection = connections[0]

                selexists = False
                for action in connection.childNodes:
                    if action.nodeType == action.ELEMENT_NODE:
                        selector = action.getAttribute('selector')
                        if selector == sel:
                            selexists = True
                            break

                if not selexists:
                    action = xmldocument.createElement('action')
                    # <action selector="messageTheBuddy:" destination="-1" eventType="touchUpInside" id="KLS-tA-9Id"/>
                    action.setAttribute('selector', sel)
                    action.setAttribute('destination', '-1')
                    action.setAttribute('eventType', 'touchUpInside')
                    action.setAttribute('id', randomidentify())
                    connection.appendChild(action)

            else:
                # this is a iboutlet property
                property = Property()
                property.name = labelname
                property.type = propertytype
                property.identify = identifiy
                properties.append(property)

    subviews = viewdom.getElementsByTagName('subviews')
    if len(subviews) > 0:
        for oneview in subviews[0].childNodes:
            if oneview.nodeType == oneview.ELEMENT_NODE:
                parseoneview(xmldocument, oneview, properties, actions)


def parsexibfile(xibfile, headerfile, implementationfile, makeacopy=False, arc=False):
    # try to get uiviews with 'userLabel' or 'accessibilityLabel'
    sc_dom = xml.dom.minidom.parse(xibfile)
    views = sc_dom.getElementsByTagName('objects')[0].getElementsByTagName('view')

    properties = []
    actions = []
    for view in views:
        parseoneview(sc_dom, view, properties, actions)

    # try to get existing iboutlet connections
    iboutlets = {}
    connections = sc_dom.getElementsByTagName('connections')
    if len(connections) > 0:
        for outlet in connections[0].childNodes:
            if outlet.nodeType == outlet.ELEMENT_NODE:
                destination = outlet.getAttribute('destination')
                identify = outlet.getAttribute('id')
                iboutlets[destination] = identify

    # generate outlets in xib file
    for oneproperty in properties:
        if not iboutlets.has_key(oneproperty.identify):
            print '<outlet property="%s" destination="%s" id="%s"/>' % (oneproperty.name, oneproperty.identify, randomidentify())
            outletelement = sc_dom.createElement('outlet')
            outletelement.setAttribute('id', randomidentify())
            outletelement.setAttribute('destination', oneproperty.identify)
            outletelement.setAttribute('property', oneproperty.name)
            connections[0].appendChild(outletelement)

    savedXib = xibfile
    if makeacopy:
        savedXib = xibfile[:-4] + '_autooutlets.xib'
    sc_dom.writexml(open(savedXib, 'w'), indent="", addindent="", newl='')

    print '\n\n'

    # process class file now
    xcodeclass = XcodeClass(headerfile, implementationfile)

    # generate iboutlet properties
    for oneproperty in properties:
        if arc:
            xcodeclass.addproperty(oneproperty.name, oneproperty.type, 'weak', True)
        else:
            xcodeclass.addproperty(oneproperty.name, oneproperty.type, 'retain', False)

    print '\n\n'

    # generate ibaction actions
    for oneaction in actions:
        xcodeclass.addmethod(oneaction)

    xcodeclass.savechanges(makeacopy)

def main(argv):
    if len(argv) == 0:
        print 'No xib file to parse'
        sys.exit(2)

    arc = False
    makeacopy = False
    xibfile = ''

    try:
        opts, args = getopt.getopt(argv, "ac", [])
    except getopt.GetoptError as err:
        print(err) # will print something like "option -a not recognized"
        sys.exit(2)
    for o, a in opts:
        if o == '-a':
            arc = True
        elif o == '-c':
            makeacopy = True
        else:
            assert False, "unhandled option"
    if len(args) > 0:
        xibfile = args[0]

    headerfile = xibfile[:-4]+'.h'
    implementationfile = xibfile[:-4]+'.m'

    if os.path.exists(xibfile):
        parsexibfile(xibfile, headerfile, implementationfile, makeacopy, arc)


if __name__ == '__main__':
    main(sys.argv[1:])
