import random
from io import BytesIO

from PIL import Image, ImageSequence


def bannerize_meme_image(image_data: bytes, is_gif: bool) -> bytes:
    """
    Converts a meme image to a Discord banner format.
    """
    image_stream = BytesIO(image_data)
    img = Image.open(image_stream)

    # Define the target size for the Discord banner
    target_width, target_height = 960, 339

    # Create a random color for the banner background
    random_color = (
        random.randint(0,
                       255),
        random.randint(0,
                       255),
        random.randint(0,
                       255),
        255
    )

    if is_gif:
        frames = []
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")
            new_frame = create_banner_from_image(
                frame,
                random_color,
                target_height,
                target_width
            )
            frames.append(new_frame)

        gif_image_stream = BytesIO()
        frames[0].save(
            gif_image_stream,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            loop=0
        )
        gif_image_stream.seek(0)
        return gif_image_stream.read()
    else:
        new_img = create_banner_from_image(
            img,
            random_color,
            target_height,
            target_width
        )
        png_image_stream = BytesIO()
        new_img.save(png_image_stream, format='PNG')
        png_image_stream.seek(0)
        return png_image_stream.read()


def create_banner_from_image(
    frame: Image.Image,
    color: tuple[float,
                 ...],
    target_height: int,
    target_width: int
) -> Image.Image:
    # Calculate the aspect ratio of the target size
    target_aspect_ratio = target_width / target_height

    # Calculate the aspect ratio of the original image
    original_aspect_ratio = frame.width / frame.height

    if original_aspect_ratio > target_aspect_ratio:
        # Resize based on width
        new_width = target_width
        new_height = int(new_width / original_aspect_ratio)
    else:
        # Resize based on height
        new_height = target_height
        new_width = int(new_height * original_aspect_ratio)

    # Resize the image to fit within the target dimensions
    frame = frame.resize((new_width, new_height), Image.LANCZOS)  # type: ignore

    # Create a new image with the target size and paste the resized frame onto it
    new_frame = Image.new("RGBA", (target_width, target_height), color)
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_frame.paste(frame, (paste_x, paste_y))

    return new_frame
