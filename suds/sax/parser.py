# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )

"""
The sax module contains a collection of classes that provide a
(D)ocument (O)bject (M)odel representation of an XML document.
The goal is to provide an easy, intuative interface for managing XML
documents.  Although, the term, DOM, is used above, this model is
B{far} better.

XML namespaces in suds are represented using a (2) element tuple
containing the prefix and the URI.  Eg: I{('tns', 'http://myns')}

"""

from logging import getLogger
import suds.metrics
from suds import *
from suds.sax import *
from suds.sax.document import Document
from suds.sax.element import Element
from suds.sax.attribute import Attribute
from suds.transport import Request
from suds.transport.http import HttpTransport
from xml.sax import parse, parseString, ContentHandler

log = getLogger(__name__)


class Handler(ContentHandler):
    """ sax hanlder """
    
    def __init__(self):
        self.nodes = [Document()]
 
    def startElement(self, name, attrs):
        top = self.top()
        node = Element(unicode(name), parent=top)
        for a in attrs.getNames():
            n = unicode(a)
            v = unicode(attrs.getValue(a))
            attribute = Attribute(n,v)
            if self.mapPrefix(node, attribute):
                continue
            node.append(attribute)
        top.append(node)
        self.push(node)
        
    def mapPrefix(self, node, attribute):
        skip = False
        if attribute.name == 'xmlns':
            if len(attribute.value):
                node.expns = attribute.value
            skip = True
        elif attribute.prefix == 'xmlns':
            prefix = attribute.name
            node.nsprefixes[prefix] = attribute.value
            skip = True
        return skip
 
    def endElement(self, name):
        name = unicode(name)
        current = self.top()
        current.setText(current.getText(trim=True))
        currentqname = current.qname()
        if name == currentqname:
            self.pop()
        else:
            raise Exception('malformed document')
 
    def characters(self, content):
        text = unicode(content)
        node = self.top()
        if node.text is None:
            node.text = text
        else:
            node.text += text

    def push(self, node):
        self.nodes.append(node)

    def pop(self):
        self.nodes.pop()
 
    def top(self):
        return self.nodes[len(self.nodes)-1]


class Parser:
    """ simple parser """
    
    def __init__(self, transport=None):
        if transport is None:
            self.transport = HttpTransport()
        else:
            self.transport = transport
        
    def parse(self, file=None, url=None, string=None):
        """ parse a document """
        handler = Handler()
        timer = metrics.Timer()
        timer.start()
        if file is not None:
            parse(file, handler)
            timer.stop()
            metrics.log.debug('sax (%s) duration: %s', file, timer)
            return handler.nodes[0]
        if url is not None:
            fp = self.transport.open(Request(url))
            parse(fp, handler)
            timer.stop()
            metrics.log.debug('sax (%s) duration: %s', url, timer)
            return handler.nodes[0]
        if string is not None:
            parseString(string, handler)
            timer.stop()
            metrics.log.debug('%s\nsax duration: %s', string, timer)
            return handler.nodes[0]

