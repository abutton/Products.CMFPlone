from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

import zLOG
import traceback
import sys

def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

_upgradePaths = {}

class MigrationTool( UniqueObject, SimpleItem):
    id = 'portal_migration'
    meta_type = 'Plone Migration Tool'

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }, )

    security = ClassSecurityInfo()
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('www/migrationTool', globals())

    security.declareProtected(ManagePortal, 'getInstanceVersion')
    def getInstanceVersion(self):
        """ The version this instance of plone is on """
        if getattr(self, '_version', None) is None:
            self.setInstanceVersion(self.getFileSystemVersion())
        return self._version

    security.declareProtected(ManagePortal, 'setInstanceVersion')
    def setInstanceVersion(self, version):
        """ The version this instance of plone is on """
        self._version = version

    security.declareProtected(ManagePortal, 'knownVersions')
    def knownVersions(self):
        """ All known version ids, except current one """
        return _upgradePaths.keys()

    security.declareProtected(ManagePortal, 'getFileSystemVersion')
    def getFileSystemVersion(self):
        """ The version this instance of plone is on """
        return self.Control_Panel.Products.CMFPlone.version

    security.declareProtected(ManagePortal, 'needUpgrading')
    def needUpgrading(self):
        """ Need upgrading? """
        return self.getInstanceVersion() != self.getFileSystemVersion()

    security.declareProtected(ManagePortal, 'upgrade')
    def upgrade(self, REQUEST=None):
        """ perform the upgrade """
        # keep it simple
        out = []
        
        # either get the forced upgrade instance or the current instance
        newv = getattr(REQUEST, "force_instance_version", self.getInstanceVersion())
       
        out.append("Starting the migration from version: %s" % newv)
        while newv is not None:
            out.append("Attempting to upgrade from: %s" % newv)
            try:
                newv = self._upgrade(newv)
                if newv is not None:
                    out.append("Upgrade to: %s, completed" % newv)
                    self.setInstanceVersion(newv)
                
            except:
                out.append('ERROR:')
                out += traceback.format_tb(sys.exc_traceback)
                out.append("Upgrade aborted")
                # set newv to None
                # to break the loop
                newv = None
                
        out.append("End of upgrade path")
        
        if self.needUpgrading():
            out.append("PROBLEM: The uppgrade path did NOT reach current version")
            out.append("Migration has failed")

        # do this once all the changes have been done
        try:
            self.portal_catalog.refreshCatalog()
            self.portal_workflow.updateRoleMappings()
        except:
            out.append("Exception was thrown while cataloging")
            pass
        return '\n'.join(out)
        

    def _upgrade(self, version):
        if not _upgradePaths.has_key(version): 
#            log('No upgrade path found for version "%s"\n' % version)
            return None

        newversion, function = _upgradePaths[version]
        function(self.aq_parent)
        return newversion


def registerUpgradePath(oldversion, newversion, function): 
    """ Basic register func """
    _upgradePaths[oldversion] = [newversion, function]

InitializeClass(MigrationTool)
