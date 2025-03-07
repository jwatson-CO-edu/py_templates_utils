# python3.11 -m pip install svgwrite CairoSVG --user

########## INIT ####################################################################################

##### Imports #####
### Special ###
import svgwrite
import cairosvg


##### Constants #####
_DOC_WIDTH_IN  =   8.5
_DOC_HEIGHT_IN =  11.0
_DOC_MARGIN_IN =   0.25
_DOC_DPI       = 300
_DOC_WIDTH_PX  = int( _DOC_WIDTH_IN  * _DOC_DPI )
_DOC_HEIGHT_PX = int( _DOC_HEIGHT_IN * _DOC_DPI )
_DOC_MARGIN_PX = int( _DOC_MARGIN_IN * _DOC_DPI )



########## DOCUMENT CREATION #######################################################################

class ResumeFactory:
    """ Create a resume """

    def __init__( self, filename = "resume.pdf" ):
        """ Set params """
        self.path = filename
        self.w_px = _DOC_WIDTH_PX
        self.h_px = _DOC_HEIGHT_PX
        self.m_px = _DOC_MARGIN_PX
        self.xMin = self.m_px
        self.xMax = self.w_px - self.m_px
        self.yMin = self.m_px
        self.yMax = self.h_px - self.m_px
        self.dSVG = svgwrite.Drawing( size = (self.w_px, self.h_px,) ) # Create SVG document
        self.dSVG.add( self.dSVG.rect( # Add a white background
            insert = (0, 0,), 
            size   = (self.w_px, self.h_px), 
            fill   ='white'
        )) 
        self.groups = dict()
        self.lstLyr = -1


    def add_layer( self, name : str, opacity : float = 1.0 ):
        """ Create a named document layer with given name and opacity """
        # NOTE: Layers are drawn in order of creation?
        self.lstLyr += 1
        self.groups[ name ] = self.dSVG.g( opacity = opacity ) # Create a group for this layer

    