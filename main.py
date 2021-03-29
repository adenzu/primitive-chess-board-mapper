import cv2
import numpy as np


# HSV value limits for pieces
WHITE_LOWER_VAL = np.array([0,  81, 17]) 
WHITE_UPPER_VAL = np.array([90,  255, 156]) 
BLACK_LOWER_VAL = np.array([100, 118, 55]) 
BLACK_UPPER_VAL = np.array([118, 255, 255]) 


# the upper left corner of the board
BOARD_RELATIVE_CORNER_COORDS = np.array([275, 95])

# number of tiles on one side of the board
BOARD_SIZE = 3



def distance(x1, y1, x2, y2):
    return ( (x1 - x2)*(x1 - x2) + (y1-y2)*(y1-y2) )**.5


# purpose was to find one tile side length automatically, doesn't work properly at the moment
def getSquareSideLength(frame):
		
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray, 50, 150, apertureSize=3)
	lines = cv2.HoughLinesP(edges, 1, np.pi/180, 200)

	lineLengths = []

	for line in lines:
		for x1, y1, x2, y2 in line:
			lineLengths.append(distance(x1, y1, x2, y2))

	return max(set(lineLengths), key=lineLengths.count)


# pixel length of one side of one tile of the board
SQUARE_SIDE_LEN = 64#getSquareSideLength(image)


# finds pixel coords of the pieces and marks on the frame and returns coords
def getPieceCoords(frame, colorLowerVal, colorUpperVal):
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)            # hsv equivalent of the frame			
	mask = cv2.inRange(hsv, colorLowerVal, colorUpperVal) 	# mask of the frame
	blurred_mask = cv2.medianBlur(mask, 15) 		# median blur to get contours more one shaped	

	cv2.imshow(str(colorLowerVal), blurred_mask)    # see piece masks respectively

        # find contours
	ret, thresh = cv2.threshold(blurred_mask,127,255,0) 
	contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	coords = []

	for c in contours:

		M = cv2.moments(c)

		if cv2.contourArea(c) < 1000 : # 1000 is upper pixel are limit for contours
			if M["m00"] != 0:
				cX = int(M["m10"] / M["m00"]) 
				cY = int(M["m01"] / M["m00"]) 

                                # append coords of pieces to the list and mark the frame accordingly
				coords.append( np.array([cX, cY]) - BOARD_RELATIVE_CORNER_COORDS )
				cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1) # circle the center of the contour
	
	return coords


# returns array equivalent of the board
def getBoardArray(frame):

	board = np.zeros([BOARD_SIZE, BOARD_SIZE])
	
	whitePieceCoords = getPieceCoords(frame, WHITE_LOWER_VAL, WHITE_UPPER_VAL)
	blackPieceCoords = getPieceCoords(frame, BLACK_LOWER_VAL, BLACK_UPPER_VAL)

        # arbitrary values, just to mark index, be sure to set different than 0
	WHITE_PIECE = 1
	BLACK_PIECE = 2

        # place the piece indicators
	for x, y in whitePieceCoords:
		xIndex = x // SQUARE_SIDE_LEN
		yIndex = y // SQUARE_SIDE_LEN

		try:
			board[yIndex][xIndex] = WHITE_PIECE
		except:
			pass
	
	for x, y in blackPieceCoords:
		xIndex = x // SQUARE_SIDE_LEN
		yIndex = y // SQUARE_SIDE_LEN

		try:
			board[yIndex][xIndex] = BLACK_PIECE
		except:
			pass

	return board

cap = cv2.VideoCapture() # your video capture device here, won't work in this form

while True:
    _, frame = cap.read()
    print(getBoardArray(frame))
    cv2.imshow("f", frame)

    if cv2.waitKey(1) & 0xff == 27:
        break
