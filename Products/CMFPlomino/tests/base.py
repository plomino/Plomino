

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_registration():
    fiveconfigure.debug_mode = True
    import Products.CMFPlomino
    zcml.load_config('configure.zcml', Products.CMFPlomino)
    fiveconfigure.debug_mode = False

    #ztc.installProduct('CMFPlomino')
    
ztc.installProduct('CMFPlomino')
setup_registration()
ptc.setupPloneSite(products=['CMFPlomino'])

