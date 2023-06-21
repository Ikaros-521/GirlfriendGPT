import logging
import re
import uuid

from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url

# 匹配UUID的字符串格式
UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)


# 检查一个字符串是否是有效的UUID。
def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check a string to see if it is actually a UUID."""
    # 将输入的字符串转换为小写
    lowered = uuid_to_test.lower()
    # 尝试使用uuid.UUID()函数将其解析为UUID对象
    try:
        uuid_obj = uuid.UUID(lowered, version=version)
    # 如果解析过程中出现异常，说明字符串不是有效的UUID，返回False。
    except ValueError:
        return False
    # 将UUID对象转换为字符串形式，并与原始字符串进行比较，如果相等，则返回True，表示是有效的UUID，否则返回False。
    return str(uuid_obj) == lowered


# 将给定的block对象上传到公共访问的块存储，并返回可读取块内容的签名URL。
def make_block_public(client, block):
    # 从block对象的mime_type属性中提取文件扩展名
    extension = block.mime_type.split("/")[1]
    # 生成一个随机的文件名，包括UUID和扩展名。
    filepath = f"{uuid.uuid4()}.{extension}"
    # 调用client.get_workspace().create_signed_url()方法创建两个签名URL，一个用于写入操作 (SignedUrl.Operation.WRITE)，一个用于读取操作 (SignedUrl.Operation.READ)。
    # 创建签名URL时，使用了指定的存储桶 (SignedUrl.Bucket.PLUGIN_DATA) 和生成的文件路径。
    signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.WRITE,
            )
        )
        .signed_url
    )
    logging.info(f"Got signed url for uploading block content: {signed_url}")
    read_signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.READ,
            )
        )
        .signed_url
    )
    # 通过调用upload_to_signed_url()函数，将block对象的原始内容上传到写入签名URL指定的位置。最后，返回读取签名URL，以便后续访问该块的内容。
    upload_to_signed_url(signed_url, block.raw())
    return read_signed_url
