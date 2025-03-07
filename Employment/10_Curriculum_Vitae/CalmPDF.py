# sudo apt install libcairo2-dev
# python3.11 -m pip install pycairo --user
# sudo ln -s /usr/lib/python3/dist-packages/cairo/_cairo.cpython-310-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/cairo/_cairo.cpython-311-x86_64-linux-gnu.so

########## INIT ####################################################################################

##### Imports #####
### Special ###
import cairo


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
        self.path    = filename
        self.w_px    = _DOC_WIDTH_PX
        self.h_px    = _DOC_HEIGHT_PX
        self.m_px    = _DOC_MARGIN_PX
        self.xMin    = self.m_px
        self.xMax    = self.w_px - self.m_px
        self.yMin    = self.m_px
        self.yMax    = self.h_px - self.m_px
        self.surface = cairo.PDFSurface( self.path, self.w_px, self.h_px )
        self.context = cairo.Context( self.surface )


    def draw_text( self, text, x, y, size = 14, color = (0.0, 0.0, 0.0) ):
        """ Draw text to the page """
        self.context.set_source_rgb( *color )
        self.context.set_font_size( size )
        self.context.move_to( x, y )
        self.context.show_text( text )


    def save( self ):
        """ Write the file """
        self.surface.finish()
        print(f"Resume saved as {self.path}")


    def render_test_01( self ):
        """ Make a document """
        self.draw_text( "James Watson", self.xMin, self.yMin, size = 14 )
        self.save()



########## MAIN ####################################################################################
if __name__ == "__main__":
    doc = ResumeFactory()
    doc.render_test_01()