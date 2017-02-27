"""
EmergencyHacks.py
James Watson , 2017 February
Self-contained functions for expedient copy-and-paste troubleshooting!
"""

# == Geometry Diagnosis ==

def points_painter( *ptsLists ):
    """ Plot some 2D points! Find out what is going on! """    
    import matplotlib.pyplot as plt
    from matplotlib import collections as mc # Simultaneous name and rename import
    def split_to_components( vecList ): 
        """ Separate a list of R^n vectors into a list of n lists of components , in order """ # because matplotlib likes it that way
        components = [ [] for dim in xrange( len( vecList[0] ) ) ] # NOTE: This function assumes that all vectors of 'vecList' are the same dimensionality
        for vec in vecList:
            for i , elem in enumerate( vec ):
                components[i].append( elem )
        return components
    def elemw( i , iterable ):
        """ Return the 'i'th index of 'iterable', wrapping to index 0 at all integer multiples of 'len(iterable)' """
        return iterable[ i % ( len( iterable ) ) ]        
    def sides_from_vertices( vertList ):
        """ Return a list of line segments from the ordered 'vertList' , consisting of each consecutive pair in a cycle with CW/CCW preserved """
        segments = [] # List of segments to be returned 
        for pDex in xrange( len( vertList ) ):
            segments.append( [ elemw( pDex , vertList ) , elemw( pDex + 1 , vertList ) ] )
        return segments                
    clrs = [ 'b' , 'g' , 'r' , 'c' , 'm' , 'y' , 'k' ]
    ax = plt.figure().add_subplot(111)
    for pDex , ptsLst in enumerate( ptsLists ):
        comp = split_to_components( ptsLst )
        ax.scatter( x = comp[0] , y = comp[1] , c = elemw( pDex , clrs ) , s = 60 , marker = "X" ) # Plot the points!
        lc = mc.LineCollection( sides_from_vertices( ptsLst ) , color = elemw( pDex , clrs ) , linewidths = 2 ) # Add criss-crossy lines!
        ax.add_collection( lc )
    plt.show()

# == End Geometry ==