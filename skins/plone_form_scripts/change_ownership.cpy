## Script (Python) "change_ownership"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=userid, subobjects=0
##title=Change ownership
##
from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

if subobjects:
    subobjects=1

context.plone_utils.changeOwnershipOf(context, userid, subobjects)

transaction_note('Changed owner of %s at %s to %s' % (context.title_or_id(), context.absolute_url(), userid))

return state.set( context = context, portal_status_message=_('Ownership has been changed.'))
