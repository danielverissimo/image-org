import math
import os
import time
import cv2
from database import withoutProcessedPaths
from constants import DEBUG

INPUT_DIR = './images'
DOWNSCALE = False

def debug(msg):
    if (DEBUG):
        print(msg)

def getInputPaths():
    absolute_input_dir = os.path.realpath(INPUT_DIR)
    input_relatives = os.listdir(INPUT_DIR)

    absolute_paths = []
    for file in input_relatives:
        absolute_paths.append(os.path.join(absolute_input_dir, file))
    
    return absolute_paths

def processFiles(paths):
    byte_count = 0

    # Load images from paths list
    image_reading_counter = time.perf_counter()
    images = []
    for path in paths:

        img = cv2.imread(path)
        w, h, colors = img.shape

        byte_count += w*h*colors

        if (DOWNSCALE and w*h > (2000*1000)):
            downscaled = (math.floor(h / 2), math.floor(w / 2))
            img = cv2.resize(cv2.imread(path), downscaled)

        images.append([path, img])
    image_reading_counter = time.perf_counter() - image_reading_counter

    debug(f'\n Read {byte_count} raw bytes image data in {image_reading_counter} seconds \n')
    
    # Check if any image contains Qr Code
    detector = cv2.QRCodeDetector()
    qr_performance_counter = time.perf_counter()
    for [path, img] in images:
        found, qr_rect = detector.detect(img)
        debug(f'{path} detected? ->{ found} rect: {qr_rect} {img.shape}')
    qr_performance_counter = time.perf_counter() - qr_performance_counter

    return [byte_count, qr_performance_counter, image_reading_counter]


if (__name__ == '__main__'):
    general_counter = time.perf_counter()

    paths = getInputPaths()

    pending_paths = withoutProcessedPaths(paths)

    sorted_paths = sorted(pending_paths, key=lambda x: x.lower())

    debug('\n SORTED AND FILTERED INPUT FILE PATHS')

    for i, path in enumerate(sorted_paths):
        debug(f'file({i}):{path}')
    
    debug ('\n Now loading images and looking for QR Codes')
    [bytes_read, qr_time, image_time] = processFiles(sorted_paths)

    debug(f'\n Read {bytes_read} bytes of raw image data and taken {qr_time} seconds to detect QR Codes, and {image_time} seconds to load images')

    general_counter = time.perf_counter() - general_counter

    print(f'\n Total time: {general_counter} seconds')