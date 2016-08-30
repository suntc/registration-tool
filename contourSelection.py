'''
Created on 2016-08-26
@author: Sun Tianchen
'''

import numpy as np
import cv2
import sys

BLUE = [255,0,0]        # rectangle color
RED = [0,0,255]         # PR BG
GREEN = [0,255,0]       # PR FG
BLACK = [0,0,0]         # sure BG
WHITE = [255,255,255]   # sure FG

DRAW_BG = {'color' : BLACK, 'val' : 0}
DRAW_FG = {'color' : WHITE, 'val' : 1}
DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
DRAW_PR_BG = {'color' : RED, 'val' : 2}

# setting up flags
rect = (0,0,1,1)
drawing = False         # flag for drawing curves
rectangle = False       # flag for drawing rect
rect_over = False       # flag to check if rect drawn
rect_or_mask = 100      # flag for selecting rect or mask mode
value = DRAW_BG         # drawing initialized to FG
thickness = 20           # brush thickness

def onmouse(event,x,y,flags,param):
	global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over

	# Draw Rectangle
	if event == cv2.EVENT_RBUTTONDOWN:
		rectangle = True
		ix,iy = x,y

	elif event == cv2.EVENT_MOUSEMOVE:
		if rectangle == True:
			img = img2.copy()
			cv2.rectangle(img,(ix,iy),(x,y),BLUE,2)
			rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
			rect_or_mask = 0

	elif event == cv2.EVENT_RBUTTONUP:
		rectangle = False
		rect_over = True
		cv2.rectangle(img,(ix,iy),(x,y),BLUE,2)
		rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
		rect_or_mask = 0
		press_n()
		print(" Now press the key 'n' a few times until no further change \n")

	# draw touchup curves

	if event == cv2.EVENT_LBUTTONDOWN:
		if rect_over == False:
			print("first draw rectangle \n")
		else:
			drawing = True
			cv2.circle(img,(x,y),thickness,value['color'],-1)
			cv2.circle(mask,(x,y),thickness,value['val'],-1)

	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing == True:
			cv2.circle(img,(x,y),thickness,value['color'],-1)
			cv2.circle(mask,(x,y),thickness,value['val'],-1)

	elif event == cv2.EVENT_LBUTTONUP:
		if drawing == True:
			drawing = False
			cv2.circle(img,(x,y),thickness,value['color'],-1)
			cv2.circle(mask,(x,y),thickness,value['val'],-1)

def press_n():
	global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over
	if (rect_or_mask == 0):         # grabcut with rect
		bgdmodel = np.zeros((1,65),np.float64)
		fgdmodel = np.zeros((1,65),np.float64)
		cv2.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv2.GC_INIT_WITH_RECT)
		rect_or_mask = 1
	elif rect_or_mask == 1:         # grabcut with mask
		bgdmodel = np.zeros((1,65),np.float64)
		fgdmodel = np.zeros((1,65),np.float64)
		cv2.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv2.GC_INIT_WITH_MASK)

def run_segmentation(image_array):
	global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over
	img = cv2.cvtColor(image_array, cv2.cv.CV_RGBA2RGB)
	img2 = img.copy()                               # a copy of original image
	mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
	output = np.zeros(img.shape,np.uint8)           # output image to be shown

	# input and output windows
	cv2.namedWindow('output')
	cv2.namedWindow('input')
	cv2.setMouseCallback('input',onmouse)
	cv2.moveWindow('input',img.shape[1]+10,90)

	print(" Instructions: \n")
	print(" Draw a rectangle around the object using right mouse button \n")
	
	bounding_rect = None
	max_contour = None
	while(1):
		
		if bounding_rect != None:
			#pass
			cv2.rectangle(output, (bounding_rect[0],bounding_rect[1]),(bounding_rect[2],bounding_rect[3]),GREEN,2)
		if max_contour != None:
			cv2.drawContours( output, max_contour, -1, (0, 255, 0), 3 )

		cv2.putText(output, "Instructions:", (8,10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED)
		cv2.putText(output, "draw a rectangle around the object with right button", (10,24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED)
		cv2.putText(output, "select areas of sure background with left button", (10,38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED)
		cv2.putText(output, "press 'r' to reset", (10,52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED)
		cv2.putText(output, "press 'esc' to exit", (10,66), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED)

		cv2.imshow('output',output)
		cv2.imshow('input',img)
		#cv2.imshow('imgray', im_gray)
		#cv2.imshow('imbw', im_bw)
		k = 0xFF & cv2.waitKey(1)

		# key bindings
		if k == 27:         # esc to exit
			break
		elif k == ord('0'): # BG drawing
			print(" mark background regions with left mouse button \n")
			value = DRAW_BG
		elif k == ord('1'): # FG drawing
			print(" mark foreground regions with left mouse button \n")
			value = DRAW_FG
		elif k == ord('2'): # PR_BG drawing
			value = DRAW_PR_BG
		elif k == ord('3'): # PR_FG drawing
			value = DRAW_PR_FG
		elif k == ord('s'): # save image
			bar = np.zeros((img.shape[0],5,3),np.uint8)
			res = np.hstack((img2,bar,img,bar,output))
			cv2.imwrite('grabcut_output.png',res)
			print(" Result saved as image \n")
		elif k == ord('r'): # reset everything
			print("resetting \n")
			rect = (0,0,1,1)
			drawing = False
			rectangle = False
			rect_or_mask = 100
			rect_over = False
			value = DRAW_FG
			img = img2.copy()
			mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
			output = np.zeros(img.shape,np.uint8)           # output image to be shown
			bounding_rect = None
			max_contour = None
		elif k == ord('n'): # segment the image
			print(""" For finer touchups, mark foreground and background after pressing keys 0-3
			and again press 'n' \n""")
			if (rect_or_mask == 0):         # grabcut with rect
				bgdmodel = np.zeros((1,65),np.float64)
				fgdmodel = np.zeros((1,65),np.float64)
				cv2.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv2.GC_INIT_WITH_RECT)
				rect_or_mask = 1
			elif rect_or_mask == 1:         # grabcut with mask
				bgdmodel = np.zeros((1,65),np.float64)
				fgdmodel = np.zeros((1,65),np.float64)
				cv2.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv2.GC_INIT_WITH_MASK)

		mask2 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
		output = cv2.bitwise_and(img2,img2,mask=mask2)
		
		#output = np.where(output!=0, 255, output)
		kernel = np.ones([20,20], np.uint8)
		im_gray = cv2.cvtColor(output.copy(),cv2.COLOR_RGB2GRAY)
		im_bw = cv2.threshold(im_gray, 1, 255, cv2.THRESH_BINARY)[1]
		im_bw = cv2.morphologyEx(im_bw, cv2.MORPH_OPEN, kernel)
		contours0 = cv2.findContours( im_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		area = 0.
		mc = None
		try:
			for c in contours0:
				cd = np.array(c)[0]
				if len(cd.shape) != 3:
					continue
				if cv2.contourArea(cd) > area:
					area = area
					max_contour = cd
			mc = max_contour.reshape(max_contour.shape[0],max_contour.shape[2])
			bounding_rect = [min(mc[:,0]),min(mc[:,1]),max(mc[:,0]),max(mc[:,1])]
		except Exception as e:
			continue

	cv2.destroyAllWindows()
	return mc

def resize_segmentation(image_array):
	max_width = 800.
	max_height = 800.
	scalar = 1.
	if image_array.shape[0] > max_height or image_array.shape[1] > max_width:
		if image_array.shape[0] / max_height > image_array.shape[1] / max_width: ## resize to meet height
			scalar = max_height / image_array.shape[0]
			img = cv2.resize(image_array, None, fx=scalar, fy=scalar)
		elif image_array.shape[0] / max_height < image_array.shape[1] / max_width: ## resize to meet width
			scalar = max_width / image_array.shape[1]
			img = cv2.resize(image_array, None, fx=scalar, fy=scalar)
	else:
		img = image_array

	mc = run_segmentation(img)
	if isinstance(mc, np.ndarray):
		mc = mc / scalar
	
	return mc
