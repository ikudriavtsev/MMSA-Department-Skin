## Script (Python) "logout"
##title=Logout handler
##parameters=
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
#temp = u''
#temp = REQUEST.URL1
#cut = temp.find('?set_language')
#if cut > 0:
    #return REQUEST.RESPONSE.redirect(REQUEST.URL1[:cut])
#else:
return REQUEST.RESPONSE.redirect(REQUEST.URL1)
