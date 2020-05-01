from tkinter import *
import time

WIDTH, HEIGHT = 80, 80

def startAgain():
	global board
	board.destroy()
	board = checkerBoard(root)

class Square(Canvas):
	"""Class for the squares on the board"""
	def __init__(self, master, squarecolor, coord, selectable=True):
		Canvas.__init__(self, master, width=75, height = 75, bg=squarecolor, borderwidth=0,highlightthickness = 0)
		if selectable:#Checks if it is a selectable square
			self.bind('<Button-1>',self.select) #Event for users click
			self.master = master #Reference to the board
			self.squareColor = squarecolor #Color of the square
			self.pieceColor = '' #Piece color that is placed on the square
			self.coords = coord #Coords of the square
			self.isSelected = False #Boolean that describes the state of the square
			self.king = False #Boolean that describes the state of the piece
			self.outline = None #the outline of the square
			self.circle = None #The circle that represents the piece

	def isKing(self):
		# Returns True if king else false
		return self.king

	def deselect(self):
		#Deselect the square
		self.outline = self.create_line(0, 0, 0, 75, 75, 75, 75, 0, 0, 0, width=4, fill=self.squareColor)
		self.isSelected = False
		# Notifies board that the square was deselected
		self.master.isSelected = False
		self.master.startPosition = (-1, -1)

	def draw(self, pieceColor, outlineColor):
		#Draws the piece of piece color with the outline of outlinecolor
		self.pieceColor = pieceColor
		self.circle = self.create_oval(5, 5, 70, 70, fill=pieceColor, width=2, outline=outlineColor)

	def clear(self):
		#Clears up the square removes all the visuals and sets some variables to defaults
		self.pieceColor = ''
		self.king = False
		self.delete('all')		

	def select(self, evt):
		# If the square is not currently selected or a multijump is available
		if not self.isSelected or self.master.multiJump:
			# If board is active and the square is empty selected checker can make a move
			if self.master.isSelected and self.pieceColor == '':
				self.master.makeMove(self.coords)# Make a move the selected square if possible
			# if (the current square is occupied ) and (the piece is of the current color) and (there is no multiJump available)
			elif self.pieceColor != '' and self.master.curColor == self.pieceColor and not self.master.multiJump:
				# If there is a piece selected
				if self.master.startPosition != (-1, -1):
					self.master.squares[self.master.startPosition].deselect()# Deselect the selected piece
				# Selects the square
				self.outline = self.create_line(0, 0, 0, 75, 75, 75, 75, 0, 0, 0, width=4)
				self.isSelected = True
				self.master.isSelected = True
				self.master.startPosition = self.coords
		else:
			#If the square is clicked twice it is deselected
			self.deselect()

	def kingenize(self):
		#Transforms a man standing on the square into a king
		self.delete('all')
		self.circle = self.create_oval(5,5,70,70, fill = self.pieceColor, width = 1,outline = 'gold')
		self.king = True

class checkerBoard(Frame):
	def __init__(self, master, initial_state = 'white'):
		Frame.__init__(self, root, highlightthickness = 0)
		self.grid()
		self.master = master

		self.isSelected = False
		self.startPosition = (-1, -1)
		self.endPosition = (-1, -1)
		self.curColor = 'white'
		self.opponentColor = 'black'
		self.multiJump = False
		self.must = False

		# A board for scores and the current player
		self.helpFrame = Frame(self)
		self.helpFrame.grid(row=8, columnspan=8)
		self.turnLabel = Label(self.helpFrame, text="  Turn:   ", font=('Arial', 24))
		self.turnLabel.grid(row=0, column=0)

		self.turnPiece = Square(self.helpFrame, 'gray', (-1,-1), selectable=False)
		self.turnPiece.grid(row=0, column=1, sticky=W+E+N+S)
		self.turnPiece.draw('white', 'black')

		self.whites = StringVar()
		self.whites.set("0")
		self.turnLabel = Label(self.helpFrame, text = "White:", font=('Arial', 24))
		self.turnLabel.grid(row=0, column = 2)
		self.turnLabel = Label(self.helpFrame, textvariable = self.whites, font=('Arial', 30), bg='white', foreground = 'black', width = 2)
		self.turnLabel.grid(row=0, column = 3)

		self.blacks = StringVar()
		self.blacks.set("0")
		self.turnLabel = Label(self.helpFrame, text = "Black:", font=('Arial', 24))
		self.turnLabel.grid(row=0, column = 4)
		self.turnLabel = Label(self.helpFrame, textvariable = self.blacks, font=('Arial', 30), bg='black',foreground = 'white',width = 2)
		self.turnLabel.grid(row=0, column = 5)

		self.squares = {}
		for row in range(8):
			for column in range(8):
				if (row + column) % 2 == 0:
					color = 'blanched almond'
					a = Square(self, color, (row, column), selectable=False)  # Creating an empty white square
					a.grid(row=row, column=column, sticky=W + E + N + S)
				else:
					color = 'dark green'
					self.squares[row, column] = Square(self, color, (row, column))
					if row < 3:  # black
						self.squares[row, column].draw('black' if initial_state == 'white' else 'white', initial_state)  # Creating a green square with a black checker
					elif row > 4:  # white
						self.squares[row, column].draw(initial_state, 'black' if initial_state == 'white' else 'white')  # Creating a green square with a white checker
					self.squares[row, column].grid(row=row, column=column, sticky=W+E+N+S)

	def flip_board(self):
		for row in range(4):
			for column in range(8):
				if (row, column) in self.squares:
					self.startPosition = (row, column)
					self.endPosition = (7 - row, 7 - column)
					self.swap()

	def makeMove(self, endPosition):
		"""A procedure which decides whether a user's move is valid
			and if it is valid makes changes"""
		self.endPosition = endPosition

		self.mustJump()
		if self.must:  # Current player has at least one jump available
			self.makeJump()
		else:  # Current player has no jump moves available
			self.makeStep()

		self.turnPiece.draw(self.curColor, self.opponentColor)  # Visually shows that the current player has been changed
		
		blackPieces = 0
		whitePieces = 0
		for square in self.squares.values():
			if square.pieceColor == 'white':
				whitePieces += 1
			elif square.pieceColor == 'black':
				blackPieces += 1
		self.blacks.set(str(12 - whitePieces))
		self.whites.set(str(12 - blackPieces))

		self.gameOver()#Checks if it is the end of the game

	def makeStep(self):
		startRow, startColumn = self.startPosition
		endRow, endColumn = self.endPosition
		if self.squares[self.startPosition].isKing():
			if abs(startColumn-endColumn) == abs(startRow-endRow):
				#################################################################
				if startRow > endRow: rows = range(startRow - 1, endRow - 1, -1)
				else: rows = range(startRow + 1, endRow + 1)
				if startColumn > endColumn: columns = range(startColumn - 1, endColumn - 1, -1)
				else: columns = range(startColumn + 1, endColumn + 1)
				#################################################################
				for row, column in zip(rows, columns):
					if self.squares[row, column].pieceColor != '':
						return
				self.swap()
				self.squares[self.endPosition].deselect()
				self.switchSides()
		else:
			if abs(startColumn-endColumn) == 1 and (endRow - startRow) == -1:
				self.swap()
				self.squares[self.endPosition].deselect()
				self.switchSides()
				if endRow == 0:
					self.squares[self.endPosition].kingenize()

	def makeJump(self):
		startRow, startColumn = self.startPosition
		endRow, endColumn = self.endPosition
		if self.squares[self.startPosition].isKing():
			if abs(startColumn - endColumn) == abs(startRow - endRow):
				count = 0  # Counter for counting pieces that a player wants to jump over
				saveRow, saveColumn = -1, -1
				###############################################################################
				if startRow > endRow: rows = range(startRow - 1, endRow, -1)
				else: rows = range(startRow + 1, endRow)
				if startColumn > endColumn: columns = range(startColumn - 1, endColumn, -1)
				else: columns = range(startColumn + 1, endColumn)
				###############################################################################
				for row, column in zip(rows, columns):
					if self.squares[row, column].pieceColor == self.opponentColor and count == 0:
						count = 1
						saveRow = row
						saveColumn = column
					elif self.squares[row, column].pieceColor != '':
						return
				if count == 0:
					return
				###########Check if it is the move that maximizes the outcome
				dr = (endRow - startRow)//abs(endRow - startRow)
				dc = (endColumn - startColumn) // abs(endColumn - startColumn)
				r = saveRow
				c = saveColumn
				nextMultiJump = False
				while (0 <= r + dr <= 7) and (0 <= c + dc <= 7):
					r = r + dr
					c = c + dc
					if self.squares[r, c].pieceColor != '':
						break
					for odr, odc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
						row = r + odr
						column = c + odc
						while (0 <= row + odr <= 7) and (0 <= column + odc <= 7) and (odr, odc) != (-dr, -dc):
							if (self.squares[row, column].pieceColor == self.opponentColor) and (self.squares[row + odr, column + odc].pieceColor == ''):
								nextMultiJump = True
								break
							elif self.squares[row, column].pieceColor != '':
								break
							row = row + odr
							column = column + odc
						if nextMultiJump: break
					if nextMultiJump: break
				#######################################
				self.checkForMultiJump(king = True)
				if nextMultiJump == self.multiJump or self.multiJump:
					self.swap()
					self.squares[saveRow, saveColumn].clear()
					self.checkForMultiJump(king = True)
					if not self.multiJump:
						self.squares[self.endPosition].deselect()
						self.switchSides()
					else:
						self.startPosition = self.endPosition
		else:
			if abs(startColumn - endColumn) == 2 and abs(endRow - startRow) == 2 and self.squares[startRow + (endRow-startRow)//2, startColumn + (endColumn-startColumn)//2].pieceColor == self.opponentColor:
				self.swap()#Swaps startPosition and endPosition squares
				self.squares[startRow + (endRow-startRow)//2, startColumn + (endColumn-startColumn)//2].clear()#Cleares the one that is in-between
				if endRow == 0:
					self.squares[self.endPosition].kingenize()
					self.multiJump = False
				else:
					self.checkForMultiJump()
				if not self.multiJump:
					self.squares[self.endPosition].deselect()
					self.switchSides()
				else:
					self.startPosition = self.endPosition

	def checkForMultiJump(self, king = False):
		self.multiJump = False
		endRow, endColumn = self.endPosition
		if king:
			for (dr, dc) in [(-1, 1),(-1, -1)]:
				r = endRow+dr
				c = endColumn+dc
				while(0 <= r+dr <= 7) and (0 <= c+dc <= 7):
					if(self.squares[r, c].pieceColor == self.opponentColor) and (self.squares[r+dr, c+dc].pieceColor == ''):
						self.multiJump = True
						return
					elif self.squares[r, c].pieceColor != '':
						break
					r = r+dr
					c = c+dc
		else:
			r, c = self.endPosition
			for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
				if (0 <= r + 2 * dr <= 7) and (0 <= c + 2 * dc <= 7):#and self.startPosition != (r + 2 * dr, c + 2 * dc):
					if (self.squares[r + dr, c + dc].pieceColor == self.opponentColor) and (self.squares[r + 2 * dr, c + 2 * dc].pieceColor == ''):
						self.multiJump = True
						return

	def mustJump(self):
		# Resetting the self.must to False, because it is always done in the beginning
		self.must = False
		for a in self.squares.values():  # Going through all the squares that a piece can be placed on
			row, column = a.coords  # Getting coordinates of a piece
			if a.pieceColor == self.curColor:  # Enter only if the piece is of the current color
				if a.isKing():  # If a piece is a king
					for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:  # Looping through all the four direction that a king can go to
						r, c = row+dr, column+dc  # Going to the next coordinate just after the position of the piece
						while(0 <= r+dr <= 7) and (0 <= c+dc <= 7):
							# If an opponent piece is on the square and a piece just after it is empty
							if (self.squares[r, c].pieceColor == self.opponentColor) and (self.squares[r + dr, c + dc].pieceColor == ''):
								# Must jump
								self.must = True
								return  # Leaves the function as it has already found that the player must jump
							# If it is either current player's piece or it is the opponents piece because the first if was not satisfied
							elif self.squares[r, c].pieceColor != '':
								break  # Only break because there might be opportunities in other directions and other pieces
							r, c = r+dr, c+dc  # Getting next coordinate
				else:
					r, c = row, column
					for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
						if (0 <= r + 2*dr <= 7) and (0 <= c + 2*dc <= 7):
							if (self.squares[r + dr, c+dc].pieceColor == self.opponentColor) and (self.squares[r + 2*dr, c + 2*dc].pieceColor == ''):
								self.must = True
								return

	def swap(self):
		""""Swaps to squares, namely startposition square with endposition square"""
		a = self.squares[self.startPosition]
		self.squares[self.startPosition] = self.squares[self.endPosition]
		self.squares[self.endPosition] = a

		self.squares[self.startPosition].coords = self.startPosition
		self.squares[self.endPosition].coords = self.endPosition

		self.squares[self.startPosition].grid(row=self.startPosition[0], column=self.startPosition[1], sticky=W+E+N+S)
		self.squares[self.endPosition].grid(row=self.endPosition[0], column=self.endPosition[1], sticky=W+E+N+S)

	def switchSides(self):
		self.master.update()
		self.master.update_idletasks()
		time.sleep(0.5)
		self.flip_board()
		# Changes the player who is currently playing
		self.curColor, self.opponentColor = self.opponentColor, self.curColor

	def gameOver(self):
		#There is gameover if all the current players pieces are removed or all pieces are blocked
		curPlayerPieces = 0
		before = self.multiJump
		for (row, column), square in self.squares.items():
			if square.pieceColor == self.curColor:
				self.endPosition = (row, column)
				self.checkForMultiJump(king = square.isKing())#Checking if the piece is blocked or not because if it is blocked it automatically does not count as a piece
				canStep = False
				#Check if it can move at least one space ahead
				for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
					if (0 <= row + dr <= 7) and (0 <= column + dc <= 7):
						if self.squares[row + dr, column + dc].pieceColor == '':
							canStep = True
							break
				if self.multiJump or canStep:
					curPlayerPieces += 1
					continue
		self.multiJump = before

		#Current player lost
		if curPlayerPieces == 0:
			self.curColor = ''#This does not allow any selection
			#Visually show win
			w, h = 300, 200
			x, y = 4 * 75 - w // 2, 4 * 75 - h // 2

			frame = Frame(root)
			frame.place(height=h, width=w, x=x, y=y)

			c = Canvas(frame, width=w, height=h, bg='white', borderwidth=0, highlightthickness=0)
			c.pack()
			c.create_line(0, 0, w, 0, w, h, 0, h, 0, 0, fill='black', width=6)

			msg = str(self.opponentColor)+" won!!!"
			lab = Label(frame, text=msg.capitalize(), font=('Calibri', 22), bg='white')
			lab.place(x=30, y=30)

			button = Button(frame, text="Start again", font=('Calibri', 14), command=startAgain, relief="flat", bd=1)
			button.place(x=30, y=110)

root = Tk()
root.title("Checkers")
root.resizable(False, False)

board = checkerBoard(root)
############Menu_bar#####################
menu = Menu(root)
root.config(menu=menu)

file = Menu(menu)
file.add_command(label="Star again", command=lambda: startAgain())
menu.add_cascade(label='Options', menu=file)
#########################################
root.mainloop()
