from zope.viewlet.interfaces import IViewletManager
from zope.schema import Text

class IBelowPortalTop(IViewletManager):
    """ A viewlet manager that sits below the <portal top> and is responsible
        for appearing of a section title.
    """

class IMmsaSearch(IViewletManager):
    """ A viewlet manager that is responsible for appearing of a search viewlet.
    """
class IMmsaLanguage(IViewletManager):
    """ A viewlet manager that is responsible for appearing of a language viewlet.
    """
class IMmsaMenu(IViewletManager):
    """ A viewlet manager that is responsible for appearing of a two-level menu.
    """
class IMmsaLeftColumn(IViewletManager):
    """ A viewlet manager that is responsible for appearing of left column navigation.
    """   
class IMmsaBar(IViewletManager):
    """ A viewlet manager that is responsible for appearing of personal bar and site actions.
    """   
class IMmsaFooter(IViewletManager):
    """ A viewlet manager that is responsible for appearing of footer.
    """    
class IMmsaPath(IViewletManager):
    """ A viewlet manager that is responsible for appearing of path.
    """
class IMmsaLogin(IViewletManager):
    """ A viewlet manager that is responsible for appearing of login link.
    """
