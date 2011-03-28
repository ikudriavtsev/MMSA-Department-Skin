from zope.interface import implements, alsoProvides
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet
from zope.deprecation.deprecation import deprecate
from zope.traversing.browser import absoluteURL
from zope.traversing.api import getParent, getPath, getParents
from zope.traversing.interfaces import IContainmentRoot

from plone.app.layout.globals.interfaces import IViewView

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner, aq_acquire
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_url,get_id,get_view_url
from cgi import escape
from urllib import quote_plus
from plone.app.layout.navigation.root import getNavigationRoot

from plone.app.i18n.locales.browser.selector import LanguageSelector
from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector

class ViewletBase(BrowserView):
    """ Base class with common functions for link viewlets.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    @property
    @deprecate("Use site_url instead. ViewletBase.portal_url will be removed in Plone 4")
    def portal_url(self):
        return self.site_url


    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.navigation_root_url = self.portal_state.navigation_root_url()

    def render(self):
        # defer to index method, because that's what gets overridden by the template ZCML attribute
        return self.index()
        
    def index(self):
        raise NotImplementedError(
            '`index` method must be implemented by subclass.')

class SiteActionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('mmsa_site_actions.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_actions = context_state.actions().get('site_actions', None)

class PersonalBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('mmsa_login.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        
        sm = getSecurityManager()

        self.user_actions = context_state.actions().get('user', None)
        for action in self.user_actions:
            if action['title'] == 'Log out':
                if action['url'].find('?set_language') > 0:
                    action['url'] = u''.join((action['url'][:action['url'].find('?set_language')],'/logout'))

        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = self.portal_state.anonymous()

        if not self.anonymous:
        
            member = self.portal_state.member()
            userid = member.getId()
            
            if sm.checkPermission('Portlets: Manage own portlets', self.context):
                self.homelink_url = self.navigation_root_url + '/dashboard'
            else:
                if userid.startswith('http:') or userid.startswith('https:'):
                    self.homelink_url = self.site_url + '/author/?author=' + userid
                else:
                    self.homelink_url = self.site_url + '/author/' + quote_plus(userid)
            
            member_info = tools.membership().getMemberInfo(member.getId())
            # member_info is None if there's no Plone user object, as when
            # using OpenID.
            if member_info:
                fullname = member_info.get('fullname', '')
            else:
                fullname = None
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid

class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('mmsa_sections.pt')

    def update(self):

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions()
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        selectedTabs = self.context.restrictedTraverse('selectedTabs')
        self.selected_tabs = selectedTabs('index_html',
                                          self.context,
                                          self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

        for tab in self.portal_tabs:
            if tab['id']!='Members':
                tab['subtab']=self.getsubtab(self.context,tab)
            else:
                tab['subtab']=[]

    def getsubtab(self,context,tab):
        query={}
        result=[]
        portal_properties = getToolByName(context, 'portal_properties')
        portal_catalog = getToolByName(context, 'portal_catalog')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        rootPath = getNavigationRoot(context)
        dpath='/'.join([rootPath,tab['id']])
        query['path'] = {'query' : dpath, 'depth' : 1}

        query['portal_type'] = utils.typesToList(context)

        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])

        query['is_default_page'] = False

        if site_properties.getProperty('disable_nonfolderish_sections', False):
            query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(**query)

        # now add the content to results
        for item in rawresult:
            if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : item.getId,
                        'url'        : item_url,
                        'description': item.Description}
                result.append(data)
        return result

class MmsaLeftColumn(ViewletBase):
    index = ViewPageTemplateFile('mmsa_left_column.pt')

    def update(self):

            context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
            actions = context_state.actions()
            portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
            self.level1 = portal_tabs_view.topLevelTabs()

            selectedTabs = self.context.restrictedTraverse('selectedTabs')
            self.selected_tabs = selectedTabs('index_html',
                                               self.context,
                                               self.level1)
            self.selected_portal_tab = self.selected_tabs['portal']

            for tab_level1 in self.level1:
                if tab_level1['id']!='Members':
                    tab_level1['level2'] = self.getsublevel(self.context,tab_level1['id'])
                    self.level2 = tab_level1['level2']
                    for tab_level2 in self.level2:
                        tab_level2['level3'] = self.getsublevel(self.context,tab_level1['id'],tab_level2['id'])
                        self.level3 = tab_level2['level3']
                        for tab_level3 in self.level3:
                            tab_level3['level4'] = self.getsublevel(self.context,tab_level1['id'],tab_level2['id'],tab_level3['id'])
                else:
                    tab_level1['level2'] = []

            path_level2 = []
            path_raw = self.context.getPhysicalPath()
            path_level2.extend(path_raw[:4])
            parent_path = '/'.join(path_level2)
            catalog = getToolByName(self.context, 'portal_catalog')
            portal_properties = getToolByName(self.context, 'portal_properties')
            navtree_properties = getattr(portal_properties, 'navtree_properties')
            raw_results = catalog.searchResults( {'path' : {'query' : parent_path, 'depth' : 0}, 'is_default_page' : False} )
            if len(raw_results):
                self.parent_id = raw_results[0].getId
            else:
                self.parent_id = u''

    def getsublevel(self, context, *path):
            query = {}
            result = []
            raw_path = []

            portal_properties = getToolByName(context, 'portal_properties')
            portal_catalog = getToolByName(context, 'portal_catalog')
            navtree_properties = getattr(portal_properties, 'navtree_properties')
            site_properties = getattr(portal_properties, 'site_properties')

            rootPath = getNavigationRoot(context)
            raw_path.append(rootPath)
            for obj in path:
                raw_path.append(obj)

            dpath='/'.join(raw_path)
            query['path'] = {'query' : dpath, 'depth' : 1}

            query['portal_type'] = ['RichDocument','Folder','GeoLocation']

            sortAttribute = navtree_properties.getProperty('sortAttribute', None)
            if sortAttribute is not None:
                query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                   query['sort_order'] = sortOrder

            if navtree_properties.getProperty('enable_wf_state_filtering', False):
                query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])

            query['is_default_page'] = False

            if site_properties.getProperty('disable_nonfolderish_sections', False) and len(path) == 1:
                query['is_folderish'] = False

            # Get ids not to list and make a dict to make the search fast
            idsNotToList = navtree_properties.getProperty('idsNotToList', ())
            excludedIds = {}
            for id in idsNotToList:
                excludedIds[id] = 1

            rawresult = portal_catalog.searchResults(**query)

            # now add the content to results
            for item in rawresult:
                if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                    id, item_url = get_view_url(item)
                    data = {'name'       : utils.pretty_title_or_id(context, item),
                            'id'         : item.getId,
                            'url'        : item_url,
                            'description': item.Description}
                    result.append(data)
            return result

class BelowPortalTop(ViewletBase):
	index = ViewPageTemplateFile('mmsa_below_portal_top.pt')

	def update(self):

        	context_state = getMultiAdapter((self.context, self.request),
                	                        name=u'plone_context_state')
	        actions = context_state.actions()
        	portal_tabs_view = getMultiAdapter((self.context, self.request),
                	                           name='portal_tabs_view')
	        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)
	
        	selectedTabs = self.context.restrictedTraverse('selectedTabs')
	        self.selected_tabs = selectedTabs('index_html',
        	                                  self.context,
                	                          self.portal_tabs)
	        self.selected_portal_tab = self.selected_tabs['portal']

class MmsaSearch(ViewletBase):
    index = ViewPageTemplateFile('mmsa_search.pt')

class MmsaLanguage(TranslatableLanguageSelector):
    render = ViewPageTemplateFile('mmsa_language.pt')
    #implements(IViewlet)

    def update(self):
            self.tool = getToolByName(self.context, 'portal_languages', None)
            portal_tool = getToolByName(self.context, 'portal_url', None)
            #self.port_url = None
            if portal_tool is not None:
                self.port_url = portal_tool.getPortalObject().absolute_url()

            self.available = TranslatableLanguageSelector.available(self)
            self.languages = []
            for language in TranslatableLanguageSelector.languages(self):
                if language['code'] == 'en':
                    language['pic'] = u'english.png'
                elif language['code'] == 'uk':
                    language['pic'] = u'ukrainian.png'
                elif language['code'] == 'ru':
                    language['pic'] = u'russian.png'
                else:
                    language['pic'] = 0
                self.languages.append(language)


class MmsaPath(ViewletBase):
        index = ViewPageTemplateFile('mmsa_path.pt')
        def update(self):
            self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            catalog = getToolByName(self.context, 'portal_catalog')
            self.context_state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
            #portal_properties = getToolByName(self.context, 'portal_properties')
            #navtree_properties = getattr(portal_properties, 'navtree_properties')
            path = []
            path_raw = self.context.getPhysicalPath()
            self.path = []
            for obj in path_raw:
                path.append(obj)
                parent_path = '/'.join(path)
                raw_results = catalog.searchResults( {'path' : {'query' : parent_path, 'depth' : 0}, 'is_default_page' : False} )
                for item in raw_results:
                    id, item_url = get_view_url(item)
                    data = {'name' : utils.pretty_title_or_id(self.context, item),
                            'url' : item_url,
                            'is_last' : False,
                            'is_suitable_view_mode' : False}
                    #try:
                        #item.getProperty('default_page')
                        #data['is_suitable_view_mode'] = True
                    #except :
                        #pass
                    if item.getObject().getProperty('default_page') is not None:
                        data['is_suitable_view_mode'] = True
                    self.path.append(data)
            if len(self.path):
                self.path[len(self.path)-1]['is_last'] = True
            self.root = self.portal_state.navigation_root_url()
            self.portal_search_url = self.root + '/search'
            self.current_page_url = self.context_state.current_page_url()
            self.view_path = True
            if self.current_page_url.count(self.portal_search_url):
                self.view_path = False


#class MmsaLogin(ViewletBase):
    #index = ViewPageTemplateFile('mmsa_login.pt')

