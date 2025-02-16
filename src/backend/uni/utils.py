#!/usr/bin/env python3

"""
uni.utils
"""

from __future__ import annotations
import hashlib
import os
import shutil
import subprocess
from typing import List, Optional, Type, Tuple
import uuid
import time
from datetime import datetime, timedelta
import re
from pydantic import BaseModel
from rich import print as rprint
from rich.table import Table
import requests
import base64
import magic
import random
import string
from PIL import Image
import io

from .exceptions import ServerError

from .logger import color_red, core_logger, log_call


logger = core_logger().getChild("utils")

# default uuid namespace
NAMESPACE_UNI: uuid.UUID = uuid.UUID("079c82c8-1327-479f-bfff-44dbabf1bb48")

def timestamp_factory(from_now: Optional[timedelta] = None) -> int:
    """ Timestamp im ms """
    # future ?
    if from_now:
        if not isinstance(from_now, timedelta): return 0

        now = datetime.now()
        return int(
            (now+from_now).timestamp() * 1000
        ) 

    # return current timestamp
    return int(
        time.time() * 1000
    )

def timestamp_to_datetime(ts: int) -> str:
    """ Convert timestamp to datetime """
    dt = datetime.fromtimestamp(ts/1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def id_factory():
    """ Returns random uuid4 """
    return uuid.uuid4()

def model_id_factory(model: Type[BaseModel], namespace: uuid.UUID = NAMESPACE_UNI) -> uuid.UUID:
    """ generates uuid5 model id """

    return uuid.uuid5(namespace, model.__name__)

def random_secret() -> str:
    return uuid.uuid4().hex

def password_hash(password: str, salt: Optional[str] = None) -> str:
    """ Generate password hash """
    if not salt:
        salt = ""

    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000,
        64
    ).hex()

def validate_email(email: str) -> str:
    """ email validation """
    if not email: raise ValueError("empty email")

    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not re.fullmatch(regex, email): raise ValueError("invalid email")

    return email

def convert_permission(p: str):
    """ convert permission from unix type(4, 2, 1) to read, write"""
    x = int(p)
    r = False
    w = False
    if x >= 4:
        r = True
        x -= 4
    if x >= 2:
        w = True

    return r, w

def download_file(url: str) -> Tuple[Optional[bytes], str]:
    """download file from url, return typle(filedata, extension)"""

    logger.info(f"Downloading file, url: {url}")

    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png"
    }

    h = requests.head(url, allow_redirects=True)
    ext = extensions.get(h.headers.get("Content-type", "_"), "")

    r = requests.get(url, allow_redirects=True)
    if not r.ok:
        logger.error(color_red(f"Error downloading file, {url}"))
        return (None, "")

    return (r.content, ext)

def save_file(data: Optional[bytes], ext: str, dir: str, filename: str) -> str:
    """ save file from bytes, return file path"""

    if not filename: return ""
    if not data: return ""
    _filename = f"{dir}/{filename}{ext}"
    logger.info(f"Saving file: {filename}")

    os.makedirs(dir, exist_ok=True)

    with open(_filename, "wb") as f:
        f.write(data)
        return filename+ext
    
def encode_file_base64(filename: str) -> str:
    """ create base64 string from file """
    r = ""

    try: 
        with open(filename, "rb") as f:
            b = base64.b64encode(f.read())
            r = str(b)
    except Exception as e:
        logger.error(color_red(f"Exception: {e}"))
        r = ""

    return r

def decode_base64_file(data: str, filename: str) -> bool:
    """ decode base64 string to file """
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
            return True
    except Exception as e:
        logger.error(color_red(f"Exception: {e}"))
        return ServerError(f"unable to decode base64 data")
    
@log_call(logger)
def shell(command) -> str:
    """runs shell command"""
    logger.info(f"shell: running command: {command}")
    r = subprocess.check_output("%s" % command, shell=True, text=True)
    logger.info(f"shell: command output: {r}")
    return r
    
@log_call(logger)
def zip_dir(filename: str, dir: str, format: str = "zip") ->  str:
    """ zip directory, return  filename"""
    if not os.path.exists(dir):
        raise ServerError(f"directory not exists: {dir}")
    return shutil.make_archive(filename, format=format, root_dir=dir )
    
@log_call(logger)
def unzip(filename: str, target_dir: str, format: str = "zip") ->  bool:
    """ unzip file to current directory"""
    if not os.path.exists(filename):
        raise ServerError(f"file not exists: {filename}")
    if not os.path.exists(target_dir):
        raise ServerError(f"directory not exists: {target_dir}")
    
    shutil.unpack_archive(filename, target_dir, format)
    return True

def get_encoding(filename: str) -> str: 
    """ returns file encoding by given filename"""
    return magic.Magic(mime_encoding=True).from_buffer(
        open(filename, 'rb').read()
    )

def random_password(length: int) -> str:
    if length < 1:
        return "Password length must be at least 1 character."
        
    # Define potential characters to use in the password
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Generate a random password
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return password


def checksum(input_string: str):
    """
    Computes the MD5 checksum of the given input string.
    Args:
        input_string (str): The input string to compute the checksum for.
    Returns:
        str: The hexadecimal digest of the MD5 checksum.
    """

    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    
    # Update the hash object with the input string
    md5_hash.update(input_string.encode('utf-8'))
    
    # Get the hexadecimal digest of the hash
    checksum = md5_hash.hexdigest()
    
    return checksum

def downscale_image(image_buffer, max_pixels):
    """
    Downscale image to have maximum number of pixels while maintaining aspect ratio
    
    Args:
        image_buffer: BufferedReader containing the image
        max_pixels: Maximum number of pixels in the output image
        
    Returns:
        BufferedReader containing the downscaled image
    """
    # Open image from buffer
    img = Image.open(image_buffer)
    
    # Get current dimensions
    width, height = img.size
    current_pixels = width * height
    
    # If image is already smaller than max_pixels, return original
    if current_pixels <= max_pixels:
        image_buffer.seek(0)  # Reset buffer position
        return image_buffer
    
    # Calculate scaling factor
    scale = (max_pixels / current_pixels) ** 0.5
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize image
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create new buffer for resized image
    output_buffer = io.BytesIO()
    
    # Save resized image to buffer in original format
    format = img.format if img.format else 'JPEG'
    resized_img.save(output_buffer, format=format)
    
    # Reset buffer position
    output_buffer.seek(0)
    
    return output_buffer

def downscale_pil_image(image: Image.Image, max_pixels: int) -> Image.Image:
    """
    Downscale image to have maximum number of pixels while maintaining aspect ratio
    
    Args:
        image: PIL Image object
        max_pixels: Maximum number of pixels in the output image
        
    Returns:
        PIL Image object containing the downscaled image
    """
    # Get current dimensions
    width, height = image.size
    current_pixels = width * height
    
    # If image is already smaller than max_pixels, return original
    if current_pixels <= max_pixels:
        return image
    
    # Calculate scaling factor
    scale = (max_pixels / current_pixels) ** 0.5
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_img

def rich_print(model: BaseModel) -> None:
    """
    Prints a detailed table representation of a Pydantic BaseModel using the rich library.
    Args:
        model (BaseModel): The Pydantic model instance to be printed.
    The function recursively traverses the fields of the model, including nested models and lists of models,
    and prints their names, values, and descriptions in a formatted table.
    """

    table = Table(title=model.__class__.__name__)
    table.add_column("Field")
    table.add_column("Value")
    table.add_column("Description")
    
    def add_fields(model: BaseModel, prefix=""):
        # Instead of using schema(), we'll use __fields__ directly
        for field_name, field in model.__fields__.items():
            value = getattr(model, field_name)
            description = field.field_info.description or "No description"
            
            if isinstance(value, BaseModel):
                # Add parent field
                table.add_row(
                    f"{prefix} {field_name}",
                    f"[cyan]{value.__class__.__name__}[/cyan]",
                    description
                )
                # Recursively add nested fields
                add_fields(value, prefix=f"{prefix}  ")
            elif isinstance(value, (list, tuple)):
                if value and isinstance(value[0], BaseModel):
                    # Handle list of BaseModels
                    table.add_row(
                        f"{prefix}, {field_name}",
                        f"List[{value[0].__class__.__name__}] (length: {len(value)})",
                        description
                    )
                    for i, item in enumerate(value):
                        add_fields(item, prefix=f"{prefix}  {i}: ")
                else:
                    # Handle regular lists
                    table.add_row(
                        f"{prefix} {field_name}",
                        str(value),
                        description
                    )
            elif value is None:
                table.add_row(
                    f"{prefix} {field_name}",
                    "[italic]None[/italic]",
                    description
                )
            else:
                # Handle regular fields
                try:
                    value_str = str(value)
                except Exception:
                    value_str = "[red]<unprintable>[/red]"
                
                table.add_row(
                    f"{prefix} {field_name}",
                    value_str,
                    description
                )
    
    try:
        add_fields(model)
        rprint(table)
    except Exception as e:
        print(f"Error while printing model: {e}")

def crawl_directory(directory: str, extensions: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    Crawls through the given directory recursively and returns a list of tuples
    containing filenames and their absolute paths.
    
    Args:
        directory (str): The root directory to start crawling.
        extensions (Optional[List[str]]): List of file extensions to filter by (e.g., ['.txt', '.py']).
                                           If None, all files will be included.
    
    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains (filename, absolute_path).
    """
    result = []
    
    # Normalize extensions to lowercase for consistent comparison
    if extensions is not None:
        extensions = [ext.lower() for ext in extensions]

    for root, dirs, files in os.walk(directory):
        for file in files:
            # Get the absolute path
            abs_path = os.path.join(root, file)

            # Check if filtering is needed
            if extensions is None or os.path.splitext(file)[1].lower() in extensions:
                result.append((file, abs_path))
    
    return result

def is_path_within_current_directory(path):
    """
    Check if a given path is within the current directory.
    Args:
        path (str): The path to check.
    Returns:
        bool: True if the path is within the current directory, False otherwise.
    """
    # Get the absolute path of the current directory
    current_directory = os.path.abspath(os.getcwd())

    # Resolve the absolute path of the given path
    target_path = os.path.abspath(path)

    # Compare the common path of both paths with the current directory
    return os.path.commonpath([current_directory]) == os.path.commonpath([current_directory, target_path])



if __name__ == '__main__': 
    exit()