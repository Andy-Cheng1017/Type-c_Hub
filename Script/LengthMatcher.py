from pcbnew import *
import wx
import math
import os

class LengthMatcher(ActionPlugin):
    class Layer:
       def __init__(self):
          self.length = 0
          self.tracks = 0
          self.imp = 0
    
    def defaults(self):
        self.name = "LengthMatcher"
        self.category = "RF, HF, Utility"
        self.description = "Finds the length of different tracks to ease in length matching"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'length_matcher.png')

    def Run(self):
        board = GetBoard() # This is to load the board inside kicad python console
        tracks = board.GetTracks()
        h = 0.035/25.4                         # to inches
        
        total = self.Layer()
        layers = dict()
        nets = set()
   
        for track in board.GetTracks():
            if track.IsSelected():
               nets.add(track.GetNet().GetNetCode())
        
        for track in board.GetTracks():
            if track.GetNet().GetNetCode() in nets:
               length = track.GetLength()/1000000
               
               imp = 0
               if length > 0:
                  w = track.GetWidth()/1000000 / 25.4     # M to mm to inches
                  inch = length/25.4                     # to inches
                  ARG1 = (2 * inch)/(w + h)
                  ARG2 = 0.2235 * (w + h) / inch
                  imp = 0.00508 * inch * (math.log(ARG1) + 0.5 + ARG2)
                  # 'Log' defaults to Natural Log.  Log10 is base 10 log
               
               total.length += length
               total.tracks += 1
               total.imp += imp
               
               if not track.GetLayer() in layers:
                  layers[track.GetLayer()] = self.Layer()
               
               layers[track.GetLayer()].length += length
               layers[track.GetLayer()].tracks += 1
               layers[track.GetLayer()].imp += imp
        
        message = 'Total:\nLength: %.4fmm\nTracks Measured: %s\nInductance: %.5fuH' % (total.length, total.tracks, total.imp)
        
        for layer, stats in layers.items():
           message += '\n\nIn Layer %s:\nLength: %.4fmm\nTracks Measured: %s\nInductance: %.5fuH' % (board.GetLayerName(layer), stats.length, stats.tracks, stats.imp)
        
        wx.MessageBox(message, 'Info',  wx.OK | wx.ICON_INFORMATION)

LengthMatcher().register() # Instantiate and register to Pcbnew