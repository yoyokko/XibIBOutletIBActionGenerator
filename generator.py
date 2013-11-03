#/usr/bin/python
__author__ = 'yoyokko@gmail.com'

import sys
import os
import xml.dom.minidom
import random

randomcharacters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')


class UIView:
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


def parseOneView(xmldocument, viewDom, uiviews):
    identifiy = viewDom.getAttribute('id')
    labelnameDesc = viewDom.getAttribute('userLabel')
    if labelnameDesc == '':
        accessibilitys = viewDom.childNodes
        for accessibility in accessibilitys:
            if accessibility.nodeType == accessibility.ELEMENT_NODE:
                keyname = accessibility.getAttribute('key')
                if keyname == 'accessibilityConfiguration':
                    labelnameDesc = accessibility.getAttribute('label')
                    break
    viewtype = 'UI' + viewDom.tagName.title()

    if viewtype.endswith('view'):
        viewtype = viewtype[:-4] + 'View'

    labelnames = labelnameDesc.split(';')

    if len(labelnames) > 0 and labelnameDesc != '':
        for labelname in labelnames:
            if labelname.startswith('SEL'):
                # this is a isaction
                # try to get connections under current xml node
                sel = labelname[4:-1]
                connections = viewDom.getElementsByTagName('connections')
                if len(connections) == 0:
                    connections = xmldocument.createElement('connections')
                    viewDom.appendChild(connections)
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
                uiview = UIView()
                uiview.name = labelname
                uiview.type = viewtype
                uiview.identify = identifiy
                uiviews.append(uiview)

    subviews = viewDom.getElementsByTagName('subviews')
    if len(subviews) > 0:
        for oneview in subviews[0].childNodes:
            if oneview.nodeType == oneview.ELEMENT_NODE:
                parseOneView(xmldocument, oneview, uiviews)


def parseXibFile(xibfile):
    # try to get uiviews with 'userLabel' or 'accessibilityLabel'
    sc_dom = xml.dom.minidom.parse(xibfile)
    views = sc_dom.getElementsByTagName('objects')[0].getElementsByTagName('view')
    uiviews = []
    for view in views:
        parseOneView(sc_dom, view, uiviews)

    # try to get existing iboutlet connections
    iboutlets = {}
    connections = sc_dom.getElementsByTagName('connections')
    if len(connections) > 0:
        for outlet in connections[0].childNodes:
            if outlet.nodeType == outlet.ELEMENT_NODE:
                destination = outlet.getAttribute('destination')
                identify = outlet.getAttribute('id')
                iboutlets[destination] = identify

    print '\n\n<!--Begin auto generated iboutlet codes-->'
    for uiview in uiviews:
        if iboutlets.has_key(uiview.identify) == False:
            print '<outlet property="%s" destination="%s" id="%s"/>' % (uiview.name, uiview.identify, randomidentify())
            outletelement = sc_dom.createElement('outlet')
            outletelement.setAttribute('id', randomidentify())
            outletelement.setAttribute('destination', uiview.identify)
            outletelement.setAttribute('property', uiview.name)
            connections[0].appendChild(outletelement)
    print '<!--End auto generated iboutlet codes-->\n'

    print '\n\n'

    savedXib = xibfile[:-4] + '_autooutlets.xib'
    sc_dom.writexml(open(savedXib, 'w'), indent="", addindent="", newl='')

    print '\n\n#pragma -- Begin auto generated iboutlet properties --'
    for uiview in uiviews:
        print '@property (nonatomic, retain) IBOutlet %s *%s;' % (uiview.type, uiview.name)
    print '#pragma -- End auto generated iboutlet properties -- \n'

    print '\n\n#pragma -- Begin auto generated iboutlet properties deallocation --'
    for uiview in uiviews:
        print '[_%s release];' % uiview.name
    print '#pragma -- End auto generated iboutlet properties deallocation -- \n'


def main(argv):
    if len(argv) == 0:
        print 'No xib file to parse'
        sys.exit(2)

    xibfile = argv[0]

    if os.path.exists(xibfile):
        parseXibFile(xibfile)


if __name__ == '__main__':
    main(sys.argv[1:])
