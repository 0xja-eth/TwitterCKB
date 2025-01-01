from io import BytesIO

import requests
from PIL import Image
from pyzbar.pyzbar import decode


def extract_invoice_from_local_qr(image_path):
    """
    Extract Lightning Network Invoice from a local QR code image file
    :param image_path: Path to the image file
    :return: Extracted invoice or None
    """
    try:
        # Open the local image file
        image = Image.open(image_path)

        # Decode the QR code using pyzbar
        decoded_objects = decode(image)

        # Iterate through the decoded results to find the invoice
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")  # Decode the QR code content
            if "fibt" in data:  # Assuming the invoice contains the "fibt" prefix
                return data

        print("No invoice found in the QR code.")
        return None

    except Exception as e:
        print(f"Error extracting invoice from QR code: {e}")
        return None


def extract_invoice_from_qr(image_url):
    """
    Extract Lightning Network Invoice from a QR code image URL
    :param image_url: URL of the image
    :return: Extracted invoice or None
    """
    try:
        # Step 1: Download the image
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        image = Image.open(BytesIO(response.content))

        # Step 2: Parse the QR code
        decoded_objects = decode(image)
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")  # Decode the QR code content
            if "fibt" in data:  # Assuming the invoice contains the "fibt" prefix
                return data

        print("No invoice found in the QR code.")
        return None

    except Exception as e:
        print(f"Error extracting invoice from QR code: {e}")
        return None
