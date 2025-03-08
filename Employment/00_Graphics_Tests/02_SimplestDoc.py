# python3.11 -m pip install svgwrite CairoSVG --user

########## INIT ####################################################################################

##### Imports #####
### Special ###
import svgwrite
import cairosvg
import numpy as np


##### Constants #####
_DOC_WIDTH_IN  =   8.5
_DOC_HEIGHT_IN =  11.0
_DOC_MARGIN_IN =   0.25
_DOC_DPI       = 300
_DOC_WIDTH_PX  = int( _DOC_WIDTH_IN  * _DOC_DPI )
_DOC_HEIGHT_PX = int( _DOC_HEIGHT_IN * _DOC_DPI )
_DOC_MARGIN_PX = int( _DOC_MARGIN_IN * _DOC_DPI )



########## DOCUMENT LAYOUT #########################################################################

class Box:
    """ Rectangular Region """

    def __init__( self, xyLocPx, xySizPx ):
        """ Set necessary parameters """
        self.xyLocPx = xyLocPx
        self.xySizPx = xySizPx

    def h_divide( self, lenList, hPadPx = -1.0 ):
        """ Horizontally devide the box """
        nuLst = list()
        N     = len(lenList)
        if hPadPx > 0.0:
            for i, len_i in enumerate( lenList ):
                nuLst.append( len_i )
                if i < (N-1):
                    nuLst.append( hPadPx )
            lenList = nuLst[:]
        tot = sum( lenList )
        lst = np.array( lenList ) / tot * self.xySizPx[0]
        if hPadPx > 0.0:
            padLen = lst[1]
        bxs = list()
        bgn = self.xyLocPx[:]
        for len_i in lst:
            if hPadPx > 0.0:
                if len_i > padLen:
                    bxs.append(  Box( bgn[:], (len_i, self.xySizPx[1],) )  )
            else:
                bxs.append(  Box( bgn[:], (len_i, self.xySizPx[1],) )  )
            bgn[0] += len_i
        return bxs



class TextBox:
    """ Block of Text """

    def __init__( self, text, xyLocPx, xySizPx, padding ):
        """ Set necessary parameters """
        self.text    = f"{text}"
        self.xyLocPx = xyLocPx
        self.xySizPx = xySizPx
        self.pad_px  = padding

    def get_text_start_abs( self ):
        """ Get the absolute location of the text start """
        return (self.xyLocPx[0]+self.pad_px, self.xyLocPx[1]+self.pad_px,)
    
    def get_max_line_length_px( self ):
        """ How long is a line of text allowed to be? """
        return self.xySizPx[0]-2*self.pad_px



########## DOCUMENT CREATION #######################################################################

class ResumeFactory:
    """ Create a resume """

    def __init__( self, filename = "resume.pdf" ):
        """ Set params """
        self.path = filename
        ## Basic Measurements ##
        self.w_px = _DOC_WIDTH_PX
        self.h_px = _DOC_HEIGHT_PX
        self.m_px = _DOC_MARGIN_PX
        self.xMin = self.m_px
        self.xMax = self.w_px - self.m_px
        self.yMin = self.m_px
        self.yMax = self.h_px - self.m_px
        ## Derived Measurements ##
        self.origin     = (self.xMin, self.yMin,)
        self.textWidth  = self.xMax - self.xMin
        self.textHeight = self.yMax - self.yMin
        ## Document + Layers ##
        self.dSVG = svgwrite.Drawing( size = (self.w_px, self.h_px,) ) # Create SVG document
        self.dSVG.add( self.dSVG.rect( # Add a white background
            insert = (0, 0,), 
            size   = (self.w_px, self.h_px), 
            fill   ='white'
        )) 
        self.groups = dict()
        self.grpDex = list()


    def save( self ):
        """ Save content in the given format """
        if len( self.grpDex ):
            for nam in self.grpDex:
                self.dSVG.add( self.groups[ nam ] )
        if ".pdf" in f"{self.path}".lower():
            svg_content = self.dSVG.tostring()
            cairosvg.svg2pdf( bytestring = svg_content, write_to = self.path )
        elif ".svg" in f"{self.path}".lower():
            self.dSVG.saveas( self.path )
        else:
            raise ValueError( f"Got path {self.path} but saving {f'{self.path}'.split('.')[-1].upper()} files is NOT SUPPORTED!" )


    def add_layer( self, name : str, opacity : float = 1.0 ):
        """ Create a named document layer with given name and opacity """
        # NOTE: Layers are added in order of creation on when `save()` is called!
        self.groups[ name ] = self.dSVG.g( opacity = opacity ) # Create a group for this layer
        self.grpDex.append( name )


    def add_text_style( self, name, size, font, color ):
        """ Add a named text style to the document """
        self.dSVG.defs.add( self.dSVG.style( f".{name} {{ font-size:{size}px; font-family:'{font}'; fill:{color} }}") )


    def add_shape_style( self, name, fillColor, strokeColor, strokeThick ):
        """ Add a named shape style to the document """
        self.dSVG.defs.add( self.dSVG.style( f'.{name} {{ fill: {fillColor}; stroke: {strokeColor}; stroke-width: {strokeThick}; }}'))


    def add_element_to_layer( self, elem, layerName = None ):
        """ Att something to a `layerName` if it exists, Otherwise add it to the base document """
        if layerName in self.groups:
            self.groups[ layerName ].add( elem )
        else:
            self.dSVG.add( elem )


    def add_styled_text( self, text, style, xyLocPx, layerName = None ):
        """ Add the `text` with the named `style` at `xyLocPx` within `layerName` if it exists """
        self.add_element_to_layer(  self.dSVG.text( text, insert = xyLocPx, class_ = style ), layerName )
        

    def add_styled_rectangle( self, xyLocPx, xySizPx, style, radius = None, layerName = None ):
        """ Add the rectangle with `xySizPx` at `xyLocPx` within `layerName` if it exists, Optional: Rounded corners with `radius` """
        self.add_element_to_layer(  
            self.dSVG.rect( insert = xyLocPx, size = xySizPx, rx = radius, ry = radius, class_ = style ), 
            layerName 
        )


    def test01( self ):
        """ Just draw anything ... """
        self.add_layer( "bio", 1.0 )
        self.add_text_style( "Title", 40, "Noto Mono Regular", "black" )
        self.add_shape_style( "MainBox", "none", "blue", 7 )
        self.add_styled_text( "James Watson", "Title", (self.xMin+self.m_px, self.yMin+self.m_px,), layerName = "bio" )
        self.add_styled_rectangle( self.origin, (self.textWidth, 300), "MainBox", radius = 40, layerName = "bio" )
        self.save()


    def test02( self ):
        """ Lay out an example document """
        _CELL_PAD =  40
        _H_ROW1   = 300
        self.add_layer( "bio", 1.0 )
        self.add_text_style( "Title", 40, "Noto Mono Regular", "black" )
        self.add_shape_style( "MainBox", "none", "blue", 7 )
        self.add_styled_rectangle( self.origin, (_H_ROW1, _H_ROW1), "MainBox", radius = 40, layerName = "bio" )
        self.add_styled_rectangle( (self.xMin+_H_ROW1+_CELL_PAD, self.yMin), (self.textWidth-2*_H_ROW1-2*_CELL_PAD, _H_ROW1), "MainBox", radius = 40, layerName = "bio" )
        self.add_styled_rectangle( (self.xMax-_H_ROW1, self.yMin), (_H_ROW1, _H_ROW1), "MainBox", radius = 40, layerName = "bio" )
        self.save()



########## MAIN ####################################################################################
if __name__ == "__main__":
    doc = ResumeFactory()
    doc.test02()
    

    