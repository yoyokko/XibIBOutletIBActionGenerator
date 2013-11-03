#/usr/bin/python

__author__ = 'yoyokko'

import os


class XcodeClass:
    def __init__(self, headerpath, implementationpath):
        self.headerpath = headerpath
        self.implementationpath = implementationpath
        self.headerstring = open(self.headerpath, 'r').read()
        self.implementationstring = open(self.implementationpath, 'r').read()
        self.classname = os.path.basename(os.path.normpath(self.headerpath)).rstrip('.h')

    def insertonelineinheader(self, tobeinsertedline, existingchecklist=[]):
        # try to find @interface classname
        interfaceindex = self.headerstring.find('@interface '+self.classname)
        if interfaceindex != -1:
            #try to find @end
            endindex = self.headerstring.find('@end', interfaceindex)
            if endindex != -1:
                # first check if we can find something in checklist
                caninsert = True
                for onecheck in existingchecklist:
                    checkindex = self.headerstring.find(onecheck, interfaceindex, endindex)
                    if checkindex != -1:
                        caninsert = False
                        break
                if caninsert:
                    # if not find, insert the property definition
                    #propertydef = '@property (nonatomic, %s) %s *%s;\n' % (propertytype, classtype, property)
                    self.headerstring = self.headerstring[:endindex] + tobeinsertedline + self.headerstring[endindex:]
                    return True
        return False

    def insertonelineinimplementation(self, tobeinsertedline, existingchecklist=[]):
        # try to find @implementation classname
        implemenationindex = self.implementationstring.find('@implementation '+self.classname)
        if implemenationindex != -1:
            #try to find @end
            endindex = self.implementationstring.find('@end', implemenationindex)
            if endindex != -1:
                # first check if we can find something in checklist
                caninsert = True
                for onecheck in existingchecklist:
                    checkindex = self.implementationstring.find(onecheck, implemenationindex, endindex)
                    if checkindex != -1:
                        caninsert = False
                        break
                if caninsert:
                    # if not find, insert the property definition
                    #propertydef = '@property (nonatomic, %s) %s *%s;\n' % (propertytype, classtype, property)
                    self.implementationstring = self.implementationstring[:endindex] + tobeinsertedline + self.implementationstring[endindex:]
                    return True
        return False

    def addmethod(self, selector=''):
        actiondesc = ''
        if selector.endswith(':'):
            actiondesc = '- (IBAction) %s(id) sender;\n' % selector
        else:
            actiondesc = '- (IBAction) %s;\n' % selector
        print actiondesc[:-1]

        self.insertonelineinheader(actiondesc, [selector])

        if selector.endswith(':'):
            actiondesc = '- (IBAction) %s(id) sender\n{\n\t\n}\n\n' % selector
        else:
            actiondesc = '- (IBAction) %s\n{\n\t\n}\n\n' % selector
        self.insertonelineinimplementation(actiondesc, [selector])

    def addproperty(self, property, classtype, propertytype, arc=False):
        # insert property definition in header file
        propertydef = '@property (nonatomic, %s) %s *%s;\n' % (propertytype, classtype, property)
        print propertydef[:-1]

        propertyinserted = self.insertonelineinheader(propertydef, [' '+property+';', '*'+property+';'])

        # insert property dealloction in implementation file
        if not arc and propertyinserted:
            # insert dealloc in implementation
            implemenationindex = self.implementationstring.find('@implementation '+self.classname)
            if implemenationindex != -1:
                deallocindex = self.implementationstring.find('dealloc', implemenationindex)

                if deallocindex == -1:
                    endindex = self.implementationstring.find('@end', implemenationindex)
                    if endindex != -1:
                        self.implementationstring = self.implementationstring[:endindex]+'\n- (void) dealloc\n{\n\t[super dealloc];\n}\n\n'+self.implementationstring[endindex:]
                        deallocindex = self.implementationstring.find('dealloc', implemenationindex)

                if deallocindex != -1:
                    deallocbegin = self.implementationstring.find('{', deallocindex)+1
                    self.implementationstring = self.implementationstring[:deallocbegin]+'\n\t[_'+property+' release]; _'+property+' = nil;'+self.implementationstring[deallocbegin:]


    def savechanges(self, makeacopy=False):
        headerpath = self.headerpath
        implementationpath = self.implementationpath

        if makeacopy:
            headerpath = headerpath[:-2]+'_autooutlets.h'
            implementationpath = implementationpath[:-2]+'_autooutlets.m'

        filehandle = open(headerpath, 'w')
        filehandle.write(self.headerstring)
        filehandle.close()

        filehandle = open(implementationpath, 'w')
        filehandle.write(self.implementationstring)
        filehandle.close()