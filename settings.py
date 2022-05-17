# Show debug messages in console?
DEBUG = True

# Persist proccess control in the internal database?
USE_DB = True

# Folder where the images to be organized are located
INPUT_DIR = './images'
# Folder where the organized groups should be created/stored
OUTPUT_DIR = './groups'

# ---- Attention, the settings below changes how the algorithm behaves ---- #

DOWNSCALE = False # If images have a volume above 2000x1000 pixels, downscale them to half their size
DELETE_PROCESSED = True # Delete processed images from the input folder
