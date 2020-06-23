# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from math import tan, pi

shoulderSet = (
	# GSGlyphsInfo.indicScripts():
	"oriya," "telugu," "cham," "kannada," "devanagari," "gujarati," "gurmukhi," "tamil," "bengali," "khmer," "malayalam", 
	# hardcoded additions:
	"arabic", "hebrew", "thai", "lao", "tibet", "myanmar"
	)

class ShowTopsAndBottoms(ReporterPlugin):
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Tops and Bottoms',
			'es': u'superiores e inferiores',
			'de': u'Höchste und tiefste Stellen',
			'nl': u'hoogste en laagste plekken',
			'fr': u'les hauts et les bas',
			'zh': u'🚧底部到顶点的数值',
		})
		
		self.keyboardShortcut = 't'
		self.keyboardShortcutModifier = NSControlKeyMask | NSCommandKeyMask | NSAlternateKeyMask
		
		Glyphs.registerDefault("com.mekkablue.ShowTopsAndBottoms.markNodesOffMetrics", True)
		self.generalContextMenus = [
			{
				'name': Glyphs.localize({
					'en': u"‘Show Tops and Bottoms’ Options:", 
					'de': u"Einstellungen für »Höchste und tiefste Stellen anzeigen«:", 
					'es': u"Opciones para ‘Mostrar superiores e inferiores’:", 
					'nl': u"Instellingen voor ‘Toon hoogste en laagste plekken’:", 
					'fr': u"Options pour «Afficher les hauts et les bas»:",
					}), 
				'action': None,
			},
			{
				'name': Glyphs.localize({
					'en': u"Mark nodes just off metric lines",
					'de': u"Punkte markieren, wenn sie die Linie knapp verpassen",
					'es': u"Marcar nodos que están cerca de la línea métrica",
					'nl': u"Punten markeren als ze net naast de hoogtes liggen",
					'fr': u"Indiquer points qui se trouvent juste à côté des lignes",
					}), 
				'action': self.toggleMarkNodesOffMetrics,
				'state': Glyphs.defaults[ "com.mekkablue.ShowTopsAndBottoms.markNodesOffMetrics" ],
			},
			]
		
	
	@objc.python_method
	def drawTop( self, bbox, drawColor, zones, xHeight, italicAngle ):
		self.drawTopOrBottom( bbox, drawColor, zones, True, xHeight, italicAngle )
	
	@objc.python_method
	def drawBottom( self, bbox, drawColor, zones, xHeight, italicAngle ):
		self.drawTopOrBottom( bbox, drawColor, zones, False, xHeight, italicAngle )
	
	@objc.python_method
	def conditionsAreMetForDrawing(self):
		"""
		Don't activate if text or pan (hand) tool are active.
		"""
		currentController = self.controller.view().window().windowController()
		if currentController:
			tool = currentController.toolDrawDelegate()
			handToolIsActive = tool.isKindOfClass_( NSClassFromString("GlyphsToolHand") )
			if not handToolIsActive: 
				return True
		return False
	
	@objc.python_method
	def drawTopOrBottom( self, bbox, defaultColor, zones, top, xHeight, italicAngle ):
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
			bboxCenterHeight = bboxOrigin.y+bboxSize.height*0.5
			offset = (position - bboxCenterHeight) * tan(italicAngle * pi / 180.0)
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
	
	@objc.python_method
	def zonesForMaster( self, master ):
		zones = [(int(z.position), int(z.size)) for z in master.alignmentZones]
		topZones = [z for z in zones if z[1] > 0]
		bottomZones = [z for z in zones if z[1] < 0]
		return topZones, bottomZones
	
	@objc.python_method
	def drawTopsAndBottoms( self, layer, defaultColor ):
		bbox = layer.bounds
		if bbox.size.height > 0.0:
			masterForTheLayer = layer.associatedFontMaster()
			if masterForTheLayer:
				xHeight = masterForTheLayer.xHeight
				italicAngle = masterForTheLayer.italicAngle
				topZones, bottomZones = self.zonesForMaster( masterForTheLayer )
				self.drawTop( bbox, defaultColor, topZones, xHeight, italicAngle )
				self.drawBottom( bbox, defaultColor, bottomZones, xHeight, italicAngle )
	
	@objc.python_method
	def drawHandleForNode(self, node):
		# calculate handle size:
		handleSizes = (5, 8, 12) # possible user settings
		handleSizeIndex = Glyphs.handleSize # user choice in Glyphs > Preferences > User Preferences > Handle Size
		handleSize = handleSizes[handleSizeIndex]*self.getScale()**-0.9 # scaled diameter
	
		# offcurves are a little smaller:
		if node.type == OFFCURVE:
			handleSize *= 0.8
	
		# selected handles are a little bigger:
		if node.selected:
			handleSize *= 1.45
	
		# draw disc inside a rectangle around point position:
		position = node.position
		rect = NSRect()
		rect.origin = NSPoint(position.x-handleSize/2, position.y-handleSize/2)
		rect.size = NSSize(handleSize, handleSize)
		NSBezierPath.bezierPathWithOvalInRect_(rect).fill()
	
	@objc.python_method
	def markNodesOffMetrics( self, layer, color=NSColor.colorWithRed_green_blue_alpha_(1.0, 0.6, 0.1, 0.7) ):
		if layer.paths:
			# set the color for drawing:
			color.set()
			
			# determine the off-heights:
			masterForTheLayer = layer.associatedFontMaster()
			glyph = layer.parent
			if glyph:
				heights = (
					1.0+masterForTheLayer.ascender if glyph.subCategory == "Lowercase" else None,
					1.0+masterForTheLayer.capHeight if glyph.subCategory != "Lowercase" else None,
					1.0+masterForTheLayer.customParameters["smallCapHeight"] if masterForTheLayer.customParameters["smallCapHeight"] and glyph.subCategory == "Smallcaps" else None,
					1.0+masterForTheLayer.customParameters["shoulderHeight"] if masterForTheLayer.customParameters["shoulderHeight"] and glyph.script in shoulderSet else None,
					1.0+masterForTheLayer.xHeight if glyph.subCategory == "Lowercase" else None,
					-1.0, # 1u below the baseline
					-1.0+masterForTheLayer.descender if glyph.subCategory == "Lowercase" else None,
				)
				for thisPath in layer.paths:
					for thisNode in thisPath.nodes:
						if thisNode.y in heights:
							self.drawHandleForNode( thisNode,  )
	
	@objc.python_method
	def foreground( self, layer ):
		if self.getScale() >= 0.05 and Glyphs.defaults["com.mekkablue.ShowTopsAndBottoms.markNodesOffMetrics"]:
			if not self.conditionsAreMetForDrawing():
				self.markNodesOffMetrics( layer )
	
	@objc.python_method
	def background( self, layer ):
		if self.getScale() >= 0.025 and self.conditionsAreMetForDrawing():
			self.drawTopsAndBottoms( layer, NSColor.darkGrayColor() )

	@objc.python_method
	def inactiveLayerForeground(self, layer):
		if self.getScale() >= 0.07 and self.conditionsAreMetForDrawing():
			self.drawTopsAndBottoms( layer, NSColor.lightGrayColor() )
			if Glyphs.defaults["com.mekkablue.ShowTopsAndBottoms.markNodesOffMetrics"]:
				self.markNodesOffMetrics( layer, color=NSColor.orangeColor() )
	
	def needsExtraMainOutlineDrawingForInactiveLayer_(self, layer):
		return True

	def toggleMarkNodesOffMetrics(self):
		self.toggleSetting("markNodesOffMetrics")
	
	@objc.python_method
	def toggleSetting(self, prefName):
		pref = "com.mekkablue.ShowTopsAndBottoms.%s" % prefName
		Glyphs.defaults[pref] = not bool(Glyphs.defaults[pref])
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	