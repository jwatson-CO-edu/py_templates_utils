_DOC_WIDTH_IN  =   8.5
_DOC_HEIGHT_IN =  11.0
_DOC_DPI       = 300
_DOC_WIDTH_PX  = int( _DOC_WIDTH_IN  * _DOC_DPI )
_DOC_HEIGHT_PX = int( _DOC_HEIGHT_IN * _DOC_DPI )

class ResumeFactory:
    """ Create a resume """

    def __init__( self, filename = "resume.pdf" ):
        """ Set params """
        self.path = filename
        self.w_px = _DOC_WIDTH_PX
        self.h_px = _DOC_HEIGHT_PX