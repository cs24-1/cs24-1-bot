from logging import Logger
from typing import Any

import easyocr
import numpy as np
from PIL import ImageSequence
from PIL.Image import Image as PILImage

from utils.constants import Constants


def get_text_from_image(logger: Logger, image_file: PILImage) -> str:
    if image_file.format == "GIF":
        image = ImageSequence.Iterator(image_file)[0].copy()
    else:
        image = image_file.copy()

    # Convert PIL image to NumPy array
    np_arr = np.array(image)

    logger.info("Starting OCR")
    reader = easyocr.Reader(
        ["de",
         "en"],
        model_storage_directory=Constants.FILE_PATHS.OCR_DATA_FOLDER
    )
    result: list[Any] = reader.readtext(np_arr)
    logger.info("Finished OCR : %s", result)
    return "\n".join([item[1] for item in result])
