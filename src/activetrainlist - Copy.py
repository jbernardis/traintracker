import wx

MENU_REMOVE_TRAIN    = 1100
MENU_CHANGE_ENGINEER = 1101
MENU_CHANGE_LOCO     = 1102
MENU_SHOW_DETAILS    = 1103
MENU_RETURN_TRAIN    = 1104

FWD_128 = 1
FWD_28 = 2
REV_128 = 3
REV_28 = 4
STOP = 5

class ActiveTrainList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(1210, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)
		
		font = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		self.SetFont(font)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Origin")
		self.InsertColumn(2, "Dir")
		self.InsertColumn(3, "Terminus")
		self.InsertColumn(4, "Engineer")
		self.InsertColumn(5, "Loco #")
		self.InsertColumn(6, "Train Description")
		self.InsertColumn(7, "Block")
		self.InsertColumn(8, "Speed")
		self.InsertColumn(9, "Limit")
		self.InsertColumn(10, "Time")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 120)
		self.SetColumnWidth(4, 120)
		self.SetColumnWidth(5, 80)
		self.SetColumnWidth(6, 340)
		self.SetColumnWidth(7, 60)
		self.SetColumnWidth(8, 70)
		self.SetColumnWidth(9, 60)
		self.SetColumnWidth(10, 80)

		self.SetItemCount(0)
		self.activeTrains = []
		self.highlight = []

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.atcA = wx.ItemAttr()
		self.atcB = wx.ItemAttr()
		self.atcA.SetBackgroundColour(wx.Colour(252, 169, 186)) # light red
		self.atcB.SetBackgroundColour(wx.Colour(251, 145, 166)) # red
		
		self.hilite = wx.ItemAttr()
		self.hilite.SetBackgroundColour(wx.Colour(0, 116, 232))
		self.hilite.SetTextColour(wx.Colour(255, 255, 255))

		self.loadImages()		
		self.il = wx.ImageList(16, 16)
		empty = self.makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxRed = self.il.Add(self.imageRed)
		self.idxGreen = self.il.Add(self.imageGreen)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self)	

	def makeBlank(self):
		empty = wx.Bitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty
	
	def loadImages(self):
		png = wx.Image("trainRed.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageRed = png
		png = wx.Image("trainGreen.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageGreen = png
		png = wx.Image("trainYellow.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageYellow = png
		
	def onRightClick(self, evt):
		self.itemSelected = self.GetFirstSelected()
		if self.itemSelected == wx.NOT_FOUND:
			return

		menu = wx.Menu()
		menu.Append( MENU_REMOVE_TRAIN, "Train at Destination" )
		menu.Append( MENU_CHANGE_ENGINEER, "Change Engineer" )
		menu.Append( MENU_CHANGE_LOCO, "Change Locomotive" )
		menu.Append( MENU_SHOW_DETAILS, "Show Train Details" )
		menu.Append( MENU_RETURN_TRAIN, "Return Train to Schedule" )
		self.Bind(wx.EVT_MENU, self.onRemoveTrain, id=MENU_REMOVE_TRAIN)
		self.Bind(wx.EVT_MENU, self.onChangeEngineer, id=MENU_CHANGE_ENGINEER)
		self.Bind(wx.EVT_MENU, self.onShowDetails, id=MENU_SHOW_DETAILS)
		self.Bind(wx.EVT_MENU, self.onChangeLoco, id=MENU_CHANGE_LOCO)
		self.Bind(wx.EVT_MENU, self.onReturnTrain, id=MENU_RETURN_TRAIN)
		self.PopupMenu( menu, evt.GetPoint() )
		menu.Destroy()
		
	def onRemoveTrain(self, evt):
		self.parent.removeActiveTrain(self.activeTrains[self.itemSelected])
		
	def onChangeEngineer(self, evt):
		self.parent.reassignTrain(self.activeTrains[self.itemSelected])
		
	def onChangeLoco(self, evt):
		self.parent.changeLoco(self.activeTrains[self.itemSelected])
		
	def onShowDetails(self, evt):
		self.parent.showDetails(self.activeTrains[self.itemSelected])
		
	def onReturnTrain(self, evt):
		self.parent.returnActiveTrain(self.activeTrains[self.itemSelected])

	def clear(self):
		self.SetItemCount(0)
		self.activeTrains = []
		self.highlight = []
		
	def count(self):
		return len(self.activeTrains)
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return None
		
		return self.activeTrains[self.selected]
			
	def setSelection(self, tx, dclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		if dclick:
			self.parent.reportDoubleClick(tx)
		else:
			self.parent.reportSelection(tx)
		
	def getTrains(self):
		return [tr["tid"] for tr in self.activeTrains]
	
	def getTrain(self, tx):
		if tx < 0 or tx >= len(self.activeTrains):
			return None
		
		return self.activeTrains[tx]
	
	def getTrainByTid(self, tid):
		for tr in self.activeTrains:
			if tr["tid"] == tid:
				return tr
			
		return None
	
	def hasTrain(self, tid):
		return self.getTrainByTid(tid) is not None
	
	def updateTrain(self, tid, loco, desc, block):
		for tx in range(len(self.activeTrains)):
			if self.activeTrains[tx]["tid"] == tid:
				if loco is not None:
					self.activeTrains[tx]["loco"] = loco
				if block is not None:
					if self.activeTrains[tx]["block"] != block:
						self.highlight[tx] = 5 # 5 second highlight time
					self.activeTrains[tx]["block"] = block
				if desc is not None:
					self.activeTrains[tx]["desc"] = desc
				self.RefreshItem(tx)
				return
		
	def addTrain(self, tr):
		tr["time"] = 0
		if "throttle" not in tr:
			tr["throttle"] = None
		if "speed" not in tr:
			tr["speed"] = None
		if "limit" not in tr:
			tr["limit"] = None
		self.activeTrains.append(tr)
		self.highlight.append(0)
		self.SetItemCount(len(self.activeTrains))
		
	def getEngineers(self):
		return [x["engineer"] for x in self.activeTrains if x["engineer"] != "ATC"]
	
	def setNewEngineer(self, neng):
		if self.selected is None:
			return False
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return False
		
		self.activeTrains[self.selected]["engineer"] = neng
		self.RefreshItem(self.selected)
		
		return True
	
	def setThrottle(self, loco, throttle, speedType, limit=None):
		tx = 0
		for tx in range(len(self.activeTrains)):
			tr = self.activeTrains[tx]
			if tr["loco"] == loco:
				self.activeTrains[tx]["throttle"] = self.formatThrottle(throttle, speedType)
				self.activeTrains[tx]["speed"] = throttle
				self.activeTrains[tx]["limit"] = limit
				self.RefreshItem(tx)
				return
			
	def formatThrottle(self, speed, speedType):
		speedStr = "%3d" % speed
		
		if speedType == FWD_128:
			return speedStr
		elif speedType == FWD_28:
			return "%s/28" % speedStr
		elif speedType == REV_128:
			return "(%s)" % speedStr
		elif speedType == REV_28:
			return "(%s/28)" % speedStr
		else:
			return speedStr
	
	def ticker(self):
		if self.GetItemCount() <= 0:
			return
		
		for tx in range(len(self.activeTrains)):
			self.activeTrains[tx]["time"] += 1
			
		self.RefreshItems(0, self.GetItemCount()-1)
		
		for tx in range(len(self.highlight)):
			if self.highlight[tx] > 0:
				self.highlight[tx] -= 1
				if self.highlight[tx] == 0:
					self.RefreshItem(tx)
		
	def delSelected(self):
		if self.selected is None:
			return False
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return False
		
		del self.activeTrains[self.selected]
		del self.highlight[self.selected]
		self.SetItemCount(len(self.activeTrains))
		self.setSelection(None)
		ct = self.GetItemCount()
		for x in range(0, ct):
			self.Select(x, on=0)
		self.RefreshItems(0, ct-1)
		return True
				
	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)
			
	def OnGetItemImage(self, item):
		if item < 0 or item >= len(self.activeTrains):
			return self.idxEmpty
		
		tr = self.activeTrains[item]
		
		if tr["throttle"] is None:
			return self.idxEmpty
		
		if tr["limit"] is None:
			return self.idxYellow
		
		if tr["speed"] > tr["limit"]:
			return self.idxRed
		
		return self.idxGreen

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.activeTrains):
			return ""
		
		tr = self.activeTrains[item]
		if col == 0:
			return tr["tid"]
		elif col == 1:
			return tr["origin"]
		elif col == 2:
			return tr["dir"]
		elif col == 3:
			return tr["terminus"]
		elif col == 4:
			return tr["engineer"]
		elif col == 5:
			if tr["loco"] is None:
				return ""
			else:
				return tr["loco"]
		elif col == 6:
			if tr["desc"] is None:
				return ""
			else:
				return tr["desc"]
		elif col == 7:
			if tr["block"] is None:
				return ""
			else:
				return tr["block"]
		elif col == 8:
			if tr["throttle"] is None:
				return ""
			else:
				return tr["throttle"]
		elif col == 9:
			if tr["limit"] is None:
				return ""
			else:
				return "%d" % tr["limit"]
		elif col == 10:
			mins = int(tr["time"] / 60)
			secs = tr["time"] % 60
			return "%2d:%02d" % (mins, secs)

	def OnGetItemAttr(self, item):
		tr = self.activeTrains[item]
		hilite = self.highlight[item] > 0
		if hilite:
			return self.hilite

		if tr["engineer"] == "ATC":
			if item % 2 == 1:
				return self.atcB
			else:
				return self.atcA
		else:
			if item % 2 == 1:
				return self.normalB
			else:
				return self.normalA