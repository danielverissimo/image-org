# Show debug messages in console?
DEBUG = True
DB_DEBUG = False

# Persist proccess control in the internal database?
USE_DB = True

# Folder where the images to be organized are located
BASE_INPUT_DIR = '/var/www/image-org-2/cameras/'
# Folder where the organized groups should be created/stored
OUTPUT_DIR = './groups'

# ---- Attention, the settings below changes how the algorithm behaves ---- #

# WARNING: Downscale is not safe right now, it will overwrite the original photo downscaled without chance of recovery.
DOWNSCALE = False # If images have a volume above 2000x1000 pixels, downscale them to half their size
DELETE_PROCESSED = False # Delete processed images from the input folder


# ------------------------------------------------------------------------- #
MAIN_STORE_FULL_PATH = True # Whether to store the fullpath or just the filename in the Main database's fotos table.
