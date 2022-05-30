import math
import os
import time
import cv2
from datetime import datetime
from database import storeGroup, withoutProcessedPaths, storeProcessedPaths, getAllCameras
from settings import DEBUG, DELETE_PROCESSED, OUTPUT_DIR, DOWNSCALE, DELETE_PROCESSED, BASE_INPUT_DIR
from slugify import slugify
from natsort import os_sorted

time.clock = time.time

run_identity = f'{time.clock()}-{datetime.now().strftime("%H:%M:%S-%d/%m/%Y")}'

def debug(msg, show=False):
    log_file = open('log.txt', 'a')

    if (DEBUG or show):
        print(msg)
    
    print(msg, file=log_file)

    log_file.close()

debug(f'\n\n--------------------------------------\nRUN {run_identity}\n')

def getInputPaths(path):
    absolute_paths = []
    file_path = BASE_INPUT_DIR + path
    if os.path.isfile(file_path):
        absolute_input_dir = os.path.realpath(file_path)
        input_relatives = os.listdir(file_path)

        for file in input_relatives:
            absolute_paths.append(os.path.join(absolute_input_dir, file))
    
    return absolute_paths

def loadImages(paths):
    images = []
    byte_count = 0
    for path in paths:

        img = cv2.imread(path)
        if hasattr(img, 'shape'):
            w, h, colors = img.shape

            byte_count += w*h*colors

            if (DOWNSCALE and w*h > (2000*1000)):
                downscaled = (math.floor(h / 2), math.floor(w / 2))
                img = cv2.resize(cv2.imread(path), downscaled)

            images.append([path, img])
    return [images, byte_count]

def categorizeImagesByQrCode(images):
    image_accumulator = []
    groups = {}
    detector = cv2.QRCodeDetector()

    debug('\tStarting QR Code detection proccess...')

    for [path, img] in images:
        found, qr_rect = detector.detect(img)
        debug(f'\t\t{path} detected? ->{ found}')

        if (found):
            qr_data = detector.decode(img, qr_rect)

            code = qr_data[0]

            debug(f'\t\t{path} code: {code}')

            if (len(code) == 0):
                debug(f'\t\t{path} invalid qrcode value, its empty')
                image_accumulator += [[path, img]]
                continue

            if (str(code) in groups):
                groups[str(code)] += image_accumulator + [[path, img]]
            else:
                groups[str(code)] = image_accumulator + [[path, img]]

            image_accumulator = []
        else:
            image_accumulator += [[path, img]]
    
    if (len(image_accumulator) > 0):
        debug('\n\t\t No QR code found in remaining images')
        for [path, img] in image_accumulator:
            debug(f'\t\t{path}')
        debug('\t\t----------------------------------------\n')
    
    if (len(groups.keys()) == 0):
        debug('\t\tNo group was created in this run.')
    
    return groups

def storeGroups(groups, camera_id, user_id):
    processed_paths = []

    for key in groups:
        debug(f'\n\t\tGroup {key} has {len(groups[key])} images \n')
        foldername = slugify(key, separator="-")

        folderpath = os.path.join(OUTPUT_DIR, foldername)

        debug(f'\t\tGroup {key}: path->{folderpath}')
         
        if (not os.path.exists(folderpath)):
            os.system(f'mkdir {folderpath}')
        else:
            debug(f'\t\tNot creating folder {foldername} for it already exists')

        if (os.path.exists(folderpath)):

            for [path, img] in groups[key]:
                processed_paths += [path]
                new_imagepath = os.path.join(folderpath, os.path.basename(path))
                cv2.imwrite(new_imagepath, img)
                debug(f'\t\tCopied {path} to {new_imagepath}')
        else:
            debug(f'\t\tSomething has gone wrong, folder {foldername} doesnt exist and couldnt be created.')
    
    if (len(processed_paths) > 0):
        debug(f'\n\t\tStoring in database which paths were copied.')
        storeProcessedPaths(processed_paths)
        debug('f\n\t\tDB DONE')

        if (DELETE_PROCESSED):
            debug('\n\t\t Deleting original files in input directory.')
            for path in processed_paths:
                if (os.path.exists(path)):
                    os.remove(path)
                    debug(f'\t\t {path} Deleted')
                else:
                    debug(f'\t\t {path} Doesnt exist, did nothing.')

    if (len(groups) > 0):
        debug('\n\t\t Calling main database to store the image groups')
        for code in groups:
            storeGroup(groups[code], code, camera_id, user_id)
        debug ('\t\t DB Done\n')

def processFiles(paths, camera_id, user_id):
    byte_count = 0
    images = []


    # ---------------------------------------------------------------------------- #

    image_reading_counter = time.perf_counter()
    [images, byte_count] = loadImages(paths)
    image_reading_counter = time.perf_counter() - image_reading_counter

    debug(f'\n\tRead {byte_count} raw bytes image data in {image_reading_counter} seconds \n')

    # ---------------------------------------------------------------------------- #

    qr_performance_counter = time.perf_counter()
    groups = categorizeImagesByQrCode(images)
    qr_performance_counter = time.perf_counter() - qr_performance_counter

    debug(f'\n\tFound {len(groups)} groups in {qr_performance_counter} seconds \n')

    # ---------------------------------------------------------------------------- #

    store_performance_counter = time.perf_counter()
    storeGroups(groups, camera_id, user_id)
    store_performance_counter = time.perf_counter() - store_performance_counter

    return [byte_count, qr_performance_counter, image_reading_counter, store_performance_counter]


if (__name__ == '__main__'):
    general_counter = time.perf_counter()

    cameras = getAllCameras()

    for camera in enumerate(cameras):
        
        debug('\nCAMERA: ' + cameraObj.diretorio)

        cameraObj = camera[1]._data[0]
        paths = getInputPaths(cameraObj.diretorio)

        # debug('\nConsulting db to discard already processed paths.\n')
        pending_paths = withoutProcessedPaths(paths)
        # debug('\nDB done\n')

        sorted_paths = os_sorted(pending_paths)

        for i, path in enumerate(sorted_paths):
            debug(f'\tfile({i}):{path}')
        
        # debug ('\nNow loading images and looking for QR Codes')
        [bytes_read, qr_time, image_time, store_time] = processFiles(sorted_paths, cameraObj.id, cameraObj.user_id)

        # debug(f'\nRead {bytes_read} bytes of raw image data\n{qr_time} seconds to detect QR Codes\n{image_time} seconds to load images\n{store_time} seconds to store images on their groups')

        general_counter = time.perf_counter() - general_counter

    debug(f'\nTotal time: {general_counter} seconds\n', True)

