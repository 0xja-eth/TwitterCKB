from io import BytesIO

import requests
from PIL import Image
from pyzbar.pyzbar import decode


def extract_invoice_from_local_qr(image_path):
    """
    从本地二维码图片文件中提取 Lightning Network Invoice
    :param image_path: 图片文件路径
    :return: 提取的 invoice 或 None
    """
    try:
        # 打开本地图片文件
        image = Image.open(image_path)

        # 使用 pyzbar 解码二维码
        decoded_objects = decode(image)

        # 遍历解码结果，寻找 invoice
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")  # 解码二维码内容
            if "fibt" in data:  # 假设 invoice 包含 "fibt" 前缀
                return data

        print("No invoice found in the QR code.")
        return None

    except Exception as e:
        print(f"Error extracting invoice from QR code: {e}")
        return None


def extract_invoice_from_qr(image_url):
    """
    从二维码图片 URL 提取 Lightning Network Invoice
    :param image_url: 图片 URL
    :return: 提取的 invoice 或 None
    """
    try:
        # Step 1: 下载图片
        response = requests.get(image_url)
        response.raise_for_status()  # 检查请求是否成功
        image = Image.open(BytesIO(response.content))

        # Step 2: 解析二维码
        decoded_objects = decode(image)
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")  # 解码二维码内容
            if "fibt" in data:  # 假设 invoice 包含 "fibt" 前缀
                return data

        print("No invoice found in the QR code.")
        return None

    except Exception as e:
        print(f"Error extracting invoice from QR code: {e}")
        return None

# image_path = "../data/test.png"
#
# invoice = extract_invoice_from_local_qr(image_path)
# print(invoice)


