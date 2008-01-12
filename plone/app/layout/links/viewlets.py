from StringIO import StringIO

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from zope.component import getMultiAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner

from plone.app.layout.viewlets import ViewletBase

from Products.CMFCore.utils import getToolByName


def get_language(context, request):
    portal_state = getMultiAdapter((context, request),
                                   name=u'plone_portal_state')
    return portal_state.locale().getLocaleID()


def render_cachekey(fun, self):
    key = StringIO()
    # Include the name of the viewlet as the underlying cache key only
    # takes the module and function name into account, but not the class
    print >> key, self.__name__
    print >> key, self.portal_url
    print >> key, get_language(aq_inner(self.context), self.request)

    return key.getvalue()


class FaviconViewlet(ViewletBase):

    _template = ViewPageTemplateFile('favicon.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())


class SearchViewlet(ViewletBase):

    _template = ViewPageTemplateFile('search.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())


class AuthorViewlet(ViewletBase):

    render = ViewPageTemplateFile('author.pt')


class NavigationViewlet(ViewletBase):

    _template = ViewPageTemplateFile('navigation.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

class RSSViewlet(ViewletBase):
    def render(self):
        syntool = getToolByName(self.context, 'portal_syndication')
        if syntool.isSyndicationAllowed(self.context):
            context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
            url = '%s/RSS' % context_state.object_url()
            return '''<link rel="alternate" href="%s" title="RSS 1.0"
                            type="application/rss+xml" />''' % url
        return ''