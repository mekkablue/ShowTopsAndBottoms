# encoding: utf-8

from pluginSTAB import *
from AppKit import *
import math

class ShowTopsAndBottoms(ReporterPluginSTAB):

	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Tops and Bottoms',
			'es': u'superiores e inferiores',
			'de': u'höchste und tiefste Stellen',
			'nl': u'hoogste en laagste plekken'
		})
		
	def drawTop( self, bbox, drawColor, zones, xHeight, italicAngle ):
		self.drawTopOrBottom( bbox, drawColor, zones, True, xHeight, italicAngle )
		
	def drawBottom( self, bbox, drawColor, zones, xHeight, italicAngle ):
		self.drawTopOrBottom( bbox, drawColor, zones, False, xHeight, italicAngle )
		
	def drawTopOrBottom( self, bbox, defaultColor, zones, top, xHeight, italicAngle ):
		try:
			bboxOrigin = bbox.origin
			bboxSize   = bbox.size
			left = bboxOrigin.x
			right = left + bboxSize.width
			middle = left + bboxSize.width / 2.0
			position = bboxOrigin.y
			
			surplus = 30.0
			scale = self.getScale()
			numberDistance = 25.0 / scale
			lineDistance = 10.0 / scale

			# adjust values for top/bottom:
			if top:
				position += bboxSize.height
				numberDistance -= 10.0 / scale
			else:
				numberDistance *= -1
				lineDistance *= -1
			
			# adjust values for italic angle:
			if italicAngle != 0.0:
				offset = (position - xHeight*0.5) * math.tan(italicAngle * math.pi / 180.0)
				left += offset
				right += offset
				middle += offset
			
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
			storedLineWidth = NSBezierPath.defaultLineWidth()
			NSBezierPath.setDefaultLineWidth_( 1.0/scale )
			
			# draw horizontal line on canvas:
			leftPoint = NSPoint( left-surplus, position )
			rightPoint = NSPoint( right+surplus, position )
			NSBezierPath.strokeLineFromPoint_toPoint_( leftPoint, rightPoint )
			
			# draw vertical line on canvas:
			startPoint = NSPoint( middle, position )
			endPoint = NSPoint( middle, position+lineDistance )
			NSBezierPath.strokeLineFromPoint_toPoint_( startPoint, endPoint )
			
			# restore default line width:
			NSBezierPath.setDefaultLineWidth_( storedLineWidth )
			
			# draw number on canvas:
			self.drawTextAtPoint( "%.1f" % position, NSPoint(middle,position+numberDistance), fontColor=drawColor )
		except Exception as e:
			self.logToConsole( "drawBottom: %s" % str(e) )
	
	def drawTopsAndBottoms( self, layer, defaultColor ):
		try:
			bbox = layer.bounds
			if bbox.size.height > 0.0:
				masterForTheLayer = layer.associatedFontMaster()
				if masterForTheLayer:
					xHeight = masterForTheLayer.xHeight
					italicAngle = masterForTheLayer.italicAngle
					zones = [(int(z.position), int(z.size)) for z in masterForTheLayer.alignmentZones]
					topZones = [z for z in zones if z[1] > 0]
					bottomZones = [z for z in zones if z[1] < 0]
					self.drawTop( bbox, defaultColor, topZones, xHeight, italicAngle )
					self.drawBottom( bbox, defaultColor, bottomZones, xHeight, italicAngle )
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
