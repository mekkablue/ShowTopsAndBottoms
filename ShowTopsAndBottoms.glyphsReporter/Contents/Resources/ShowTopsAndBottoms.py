# encoding: utf-8


from plugin import *
from AppKit import *



class ShowTopsAndBottoms(ReporterPluginTopBottom):

	def settings(self):
		self.menuName = 'Tops and Bottoms'
		
	def drawForeground(self, layer):
		pass

	def drawTop( self, bbox, drawColor, zones ):
		self.drawTopOrBottom( bbox, drawColor, zones, True )
		
	def drawBottom( self, bbox, drawColor, zones ):
		self.drawTopOrBottom( bbox, drawColor, zones, False )
		
	def drawTopOrBottom( self, bbox, defaultColor, zones, top ):
		try:
			bboxOrigin = bbox.origin
			bboxSize   = bbox.size
			left = bboxOrigin.x
			right = left + bboxSize.width
			middle = left + bboxSize.width / 2.0
			position = bboxOrigin.y
			
			offset = 20.0
			surplus = 30.0
			scale = self.getScale()
			numberDistance = (offset+5.0) / scale
			lineDistance = (offset-10.0) / scale

			# adjust values for top/bottom:
			if top:
				position += bboxSize.height
				numberDistance -= 10.0 / scale
			else:
				numberDistance *= -1
				lineDistance *= -1
			
			# brings macro window to front and clears its log:
			
			
			# draw it red if it is not inside a zone:
			drawColor = NSColor.redColor()
			for thisZone in zones:
				zoneBegin = thisZone[0]
				zoneEnd = zoneBegin + thisZone[1]
				zoneBottom = min( ( zoneBegin, zoneEnd ) )
				zoneTop = max( ( zoneBegin, zoneEnd ) )
				if position <= zoneTop and position >= zoneBottom:
					drawColor = defaultColor

			# set line attributes:
			drawColor.set()
			NSBezierPath.setDefaultLineWidth_( 1.0/scale )
			
			# draw horizontal line on canvas:
			leftPoint = NSPoint( left-surplus, position )
			rightPoint = NSPoint( right+surplus, position )
			NSBezierPath.strokeLineFromPoint_toPoint_( leftPoint, rightPoint )
			
			# draw vertical line on canvas:
			startPoint = NSPoint( middle, position )
			endPoint = NSPoint( middle, position+lineDistance )
			NSBezierPath.strokeLineFromPoint_toPoint_( startPoint, endPoint )
			
			# draw number on canvas:
			self.drawTextAtPoint( "%.1f" % position, NSPoint(middle,position+numberDistance), fontColor=drawColor )
		except Exception as e:
			self.logToConsole( "drawBottom: %s" % str(e) )
	
	def drawTopsAndBottoms( self, layer, defaultColor ):
		try:
			bbox = layer.bounds
			if bbox.size.height > 0.0:
				zones = [(int(z.position), int(z.size)) for z in layer.associatedFontMaster().alignmentZones]
				topZones = [z for z in zones if z[1] > 0]
				bottomZones = [z for z in zones if z[1] < 0]
				self.drawTop( bbox, defaultColor, topZones )
				self.drawBottom( bbox, defaultColor, bottomZones )
		except Exception as e:
			self.logToConsole( "drawTopsAndBottoms: %s" % str(e) )
	
	def drawBackground( self, layer ):
		try:
			self.drawTopsAndBottoms( layer, NSColor.darkGrayColor() )
		except Exception as e:
			self.logToConsole( "drawBackground: %s" % str(e) )

	def drawBackgroundForInactiveLayers(self, layer):
		try:
			self.drawTopsAndBottoms( layer, NSColor.lightGrayColor() )
		except Exception as e:
			self.logToConsole( "drawBackgroundForInactiveLayers: %s" % str(e) )

	def drawPreview(self, layer):
		pass
