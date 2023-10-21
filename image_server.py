import os
import uuid
import logging
from werkzeug.datastructures import FileStorage

class ImageServer:
    def __init__(self, image_folder: str) -> None:
        os.makedirs(image_folder, exist_ok=True)
        self.image_folder = image_folder

    def store_image(self, image: FileStorage) -> dict:
        filename_on_server = str(uuid.uuid4())
        image.save(os.path.join(self.image_folder, filename_on_server))
        return {'filename': image.filename, 'filenameOnServer': filename_on_server}

    def store_images(self, images: list[FileStorage]) -> list[dict]:
        files = []
        for image in images:
            if image.filename != '':
                files.append(self.store_image(image))
        return files
    
    def remove_image(self, image: str):
        full_path = os.path.join(self.image_folder, image)
        try:
            os.remove(full_path) 
        except FileNotFoundError:
            logging.warning(f"Image not found on server: '{full_path}'")


    def remove_images(self, images: list[dict]):
        for image in images:
            self.remove_image(image['filenameOnServer'])