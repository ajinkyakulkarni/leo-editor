#@+leo-ver=5-thin
#@+node:tbrown.20070322113635: * @file bookmarks.py
#@+<< docstring >>
#@+node:tbrown.20070322113635.1: ** << docstring >>
''' Supports @bookmarks nodes with url's in body text.

Below a node with @bookmarks in the title, double-clicking the headline of any
node will attempt to open the url in the first line of the body-text. For lists
of bookmarks (including UNLs) this gives a clean presentation with no '@url'
markup repeated on every line etc.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@+<< version history >>
#@+node:tbrown.20070322113635.2: ** << version history >>
#@+at
# 0.1 -- first release - TNB
#@-<< version history >>
#@+<< imports >>
#@+node:tbrown.20070322113635.3: ** << imports >>
import leo.core.leoGlobals as g

use_qt = False
if g.app.gui.guiName() == 'qt':
    try:
        from PyQt4 import QtGui, QtCore
        import hashlib
        use_qt = True
    except ImportError:
        use_qt = False


#@-<< imports >>

#@+others
#@+node:ekr.20100128073941.5371: ** init
def init():

    g.registerHandler("icondclick1", onDClick1)

    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20070322113635.4: ** onDClick1
def onDClick1 (tag,keywords):

    c = keywords.get("c")
    p = keywords.get("p")
    bookmark = False
    for nd in p.parents():
        if '@bookmarks' in nd.h:
            bookmark = True
            break
    if bookmark:
        # Get the url from the first body line.
        lines = p.b.split('\n')
        url = lines and lines[0] or ''
        if not g.doHook("@url1",c=c,p=p,v=p,url=url):
            g.handleUrlInUrlNode(url,c=c,p=p)
        g.doHook("@url2",c=c,p=p,v=p)
        return 'break'
    else:
        return None
#@+node:tbrown.20110712100955.39215: ** command bookmarks_show
@g.command('bookmarks_show')
def bookmarks_show(event):
    if use_qt:
        BookMarkDisplay(event['c'])
    else:
        g.es("Requires Qt GUI")
#@+node:tbrown.20110712100955.18924: ** class BookMarkDisplay
class BookMarkDisplay:
    
    #@+others
    #@+node:tbrown.20110712100955.18926: *3* __init__
    def __init__(self, c):
        
        self.c = c
        self.v = c.p.v
        
        if hasattr(c, 'free_layout') and hasattr(c.free_layout, 'get_top_splitter'):
            # FIXME, second hasattr temporary until free_layout merges with trunk
            self.w = QtGui.QWidget()
            c.free_layout.get_top_splitter().add_adjacent(self.w, 'bodyFrame', 'left-of')
        else:
            c.frame.log.createTab(c.p.h[:10])
            tabWidget = c.frame.log.tabWidget
            self.w = tabWidget.widget(tabWidget.count()-1)
        
        self.w.setLayout(QtGui.QVBoxLayout())
        self.w.layout().setContentsMargins(0,0,0,0)

        self.current_list = self.get_list()
        
        self.show_list(self.current_list)
        
        g.registerHandler('select1', self.update)
    #@+node:tbrown.20110712100955.18925: *3* color
    def color(self, text):
        """make a consistent light background color for text"""
        x = hashlib.md5(text).hexdigest()[-6:]
        x = tuple([int(x[2*i:2*i+2], 16)//4+int('bb',16) for i in range(3)])
        x = '%02x%02x%02x' % x
        return x
    #@+node:tbrown.20110712100955.39216: *3* get_list
    def get_list(self):
        
        p = self.c.vnode2position(self.v)
        if not p:
            return
        
        return [(i.h, i.b.split('\n', 1)[0])
                for i in p.subtree()]
    #@+node:tbrown.20110712100955.39217: *3* show_list
    def show_list(self, links):
        
        p = self.c.vnode2position(self.v)
        if not p:
            return
        
        w = self.w
        
        for i in range(w.layout().count()-1, -1, -1):
            w.layout().removeItem(w.layout().itemAt(i))
       
        te = QtGui.QTextBrowser()
        w.layout().addWidget(te)
        te.setReadOnly(True)
        te.setOpenLinks(False)
        
        def anchorClicked(url, c=self.c, p=p):
            g.handleUrlInUrlNode(str(url.toString()), c=c, p=p)
        
        te.connect(te, QtCore.SIGNAL("anchorClicked(const QUrl &)"), anchorClicked)
        
        html = []
        
        for name, link in links:
            html.append("<a href='%s' style='background: #%s; color: black; text-decoration: none;'>%s</a>"
                % (link, self.color(name), name.replace(' ', '&nbsp;')))
        
        html = '\n'.join(html)
        
        te.setHtml(html)
    #@+node:tbrown.20110712100955.39218: *3* update
    def update(self, tag, keywords):
        
        if keywords['c'] is not self.c:
            return

        l = self.get_list()
        if l != self.current_list:
            self.current_list = l
            self.show_list(self.current_list)
        
        return None  # do not stop processing the select1 hook
    #@-others
#@-others
#@-leo
