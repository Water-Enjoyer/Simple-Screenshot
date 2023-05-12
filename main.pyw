import os
from time import sleep
import keyboard
import requests
import cv2 as cv
import webbrowser
import numpy as np
import pyperclip as pc
from PIL import ImageGrab
from datetime import datetime

DIR_TO_SAVE_IMGS = r""


# handles all mouse detection
def mouse_crop(event, x, y, flags, window_id):
    global coords, crop, drawing, left_image_copy, right_image_copy

    # if it's the second window, push it over
    if window_id:
        x += half

    # logs coords on mouse events
    if event == cv.EVENT_LBUTTONDOWN:
        coords = [(x, y)]
        drawing = True
    elif event == cv.EVENT_LBUTTONUP:
        coords.append((x, y))
        crop = True
        drawing = False

    # draws rectangle
    elif event == cv.EVENT_MOUSEMOVE and drawing:
        start_x = coords[0][0]
        start_y = coords[0][1]
        left_image_copy = left_image.copy()
        right_image_copy = right_image.copy()
        cv.rectangle(left_image_copy, (start_x, start_y), (x, y), (0, 0, 255), 3)
        cv.rectangle(right_image_copy, (start_x - half, start_y), (x - half, y), (0, 0, 255), 3)
        cv.imshow("Image", left_image_copy)
        cv.imshow("Image2", right_image_copy)


while True:
    sleep(0.01)
    if keyboard.is_pressed("print screen"):

        # sets globals on each key press
        coords = []
        crop = False
        drawing = False

        # takes screenshot, converts to numpy array for opencv
        img_pil = ImageGrab.grab(all_screens=True)
        img_pil.convert('RGB')
        img = np.array(img_pil)
        # swap the R and B from RGB to BGR
        img = img[:, :, ::-1].copy()

        # splits image down the middle, makes a left and right side copy
        h, w, channels = img.shape
        half = w//2
        left_image = img[:, :half]
        right_image = img[:, half:]
        left_image_copy = left_image.copy()
        right_image_copy = right_image.copy()

        # opens windows, positions them correctly
        cv.startWindowThread()

        cv.namedWindow("image", cv.WINDOW_NORMAL)
        cv.setWindowProperty("image", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

        cv.moveWindow("image", 0 - half, 0)

        cv.namedWindow("image2", cv.WINDOW_NORMAL)
        cv.setWindowProperty("image2", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

        cv.moveWindow("image2", 0, 0)

        # mouse crop callback to determine when the mouse is clicked and let go
        cv.setMouseCallback("image", mouse_crop, 0)
        cv.setMouseCallback("image2", mouse_crop, 1)

        # force image windows to top
        cv.setWindowProperty("image", cv.WND_PROP_TOPMOST, 1)
        cv.setWindowProperty("image2", cv.WND_PROP_TOPMOST, 1)

        # outlines screenshot preview in red
        cv.rectangle(left_image_copy, (0, 0), (w, h), (0, 0, 255), 5)
        cv.rectangle(right_image_copy, (-w, 0), (w//2, h), (0, 0, 255), 5)

        while True:
            # displays images
            cv.imshow("image", left_image_copy)
            cv.imshow("image2", right_image_copy)

            # break once mouse callback has set global crop to True
            if crop:
                break

            # "checks" for mouse crop every 250ms, cancels on escape
            if cv.waitKey(250) == 27:
                break
        # closes all windows once cropped
        cv.destroyAllWindows()

        # deals with escape
        if len(coords) != 2:
            continue

        # fixes mouse coordinates for lower right to top left
        if coords[0][0] > coords[1][0]:
            coords.reverse()

        # fixes mouse coordinates for lower left to top right
        if coords[0][1] > coords[1][1]:
            top = coords[1][1]
            bottom = coords[0][1]
            left = coords[0][0]
            right = coords[1][0]
            coords = [(left, top), (right, bottom)]

        # crops the image
        crop = img[coords[0][1]:coords[1][1], coords[0][0]:coords[1][0]]

        # sets name for image to be saved as
        now = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        filename = f"{now}.png"
        filepath = os.path.join(DIR_TO_SAVE_IMGS, filename)

        # saves image as file
        cv.imwrite(filepath, crop)

        # uploads the cropped screenshot to catbox
        with open(filepath, 'rb') as f:
            url = 'https://litterbox.catbox.moe/resources/internals/api.php'
            file = {'fileToUpload': f}
            data = {'reqtype': 'fileupload', 'time': '1h'}

            # gets link from response
            link = requests.post(url, data=data, files=file).text

        # copies link to clipboard and opens in default browser
        pc.copy(link)
        webbrowser.open(link)
