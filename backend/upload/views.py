import os
import io
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Util import Counter
from Crypto.Hash import SHA256, HMAC, SHA1
from PIL import Image


# TODO: consider placing encrypt_image function
# in a utils file/class and import it here
def encrypt_image(input_image_path, output_image_path, key):
    image = Image.open(input_image_path)

    iv = get_random_bytes(AES.block_size)

    image_hash = SHA256.new(
        os.path.basename(input_image_path).encode("utf=8")).hexdigest()

    key_specific = HMAC.new(key,
                            msg=image_hash.encode("utf-8"),
                            digestmod=SHA256).digest()

    unique_iv = HMAC.new(key_specific, msg=os.urandom(16),
                         digestmod=SHA256).digest()[:16]

    if len(unique_iv) != 16:
        raise ValueError("Unexpected IV length. Encryption aborted.")

    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format=image.format)
    img_bytes = img_byte_array.getvalue()

    cipher = AES.new(key, AES.MODE_CBC, unique_iv)

    padded_data = pad(img_bytes, AES.block_size)
    encrypted_data = iv + cipher.encrypt(padded_data)

    with open(output_image_path, 'wb') as f:
        f.write(encrypted_data)

    iv_path = os.path.join(os.path.dirname(output_image_path),
                           f"{os.path.basename(input_image_path)}.iv")
    with open(iv_path, 'wb') as f:
        f.write(unique_iv)

    print(
        f"Encryption successful. Encrypted image saved to '{output_image_path}'"
    )
    print(f"IV file saved to '{iv_path}'.")


def decrypt_image(input_image_path, output_image_path, key, iv_path):
    with open(iv_path, 'rb') as f:
        unique_iv = f.read()

    with open(input_image_path, 'rb') as f:
        encrypted_data = f.read()

    iv = encrypted_data[:AES.block_size]
    encrypted_data = encrypted_data[AES.block_size:]

    cipher = AES.new(key, AES.MODE_CBC, unique_iv)

    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    decrypted_image = Image.open(io.BytesIO(decrypted_data))

    decrypted_image.save(output_image_path, format=decrypted_image.format)

    print(
        f"Decryption successful. Decrypted image saved to '{output_image_path}'."
    )


#TODO: remove csrf exemption once way is found
# to have csrf sent in request headers (i.e. user is logged in)
@csrf_exempt
def index(request):
    # TODO: change key to UUID unique to User Id and/or Album Name
    # which should be stored in DB
    key = 'UZ4i59vPgLRT16s8FZ4i81vPgLRT16qk'
    key = bytes(key, encoding="utf=8")

    if request.method == "POST":
        if request.FILES.get("image", None) is not None:
            img = request.FILES["image"]
            # TODO: adjust location and image paths to dynamically change
            # based off of User ID and Album name
            location = "media/images"
            os.makedirs(location, exist_ok=True)
            fs = FileSystemStorage(location)
            fs.save(img.name, img)
            input_image_path = location + "/" + img.name
            output_image_path = location + "/" + "encrypted_" + img.name
            encrypt_image(input_image_path, output_image_path, key)
            # Removes unencrypted files
            os.remove(input_image_path)
            return JsonResponse({'msg': 'image received.'})

    # TODO: for clarity, separate this and decrypt_image out into a separate file/route
    if request.method == "GET":
        img_dir = os.fsencode('./media/images/')
        image_filenames = []

        # Decrypts all files within /media/images starting with encrypted_
        # Requires use of corresponding .iv file created from encrypt_image
        for file in os.listdir(img_dir):
            filename = os.fsdecode(file)
            if filename.startswith("encrypted"):
                decrypted_file_name = filename.split("encrypted_")[1]
                iv_file = decrypted_file_name + ".iv"
                decrypt_image("./media/images/" + filename,
                              "./media/images/" + decrypted_file_name, key,
                              "./media/images/" + iv_file)

        # Looks for all .jpg files in media/images that don't started with "encrypted"
        # TODO: append endswith() clauses to check for
        # ".png", ".jpeg" and other image file formats
        for file in os.listdir(img_dir):
            filename = os.fsdecode(file)
            if filename.endswith(
                    ".jpg") and not filename.startswith("encrypted"):
                with open("media/images/" + filename, "rb") as image_file:
                    image_data = base64.b64encode(
                        image_file.read()).decode('utf-8')
                image_filenames.append(image_data)

        # Removes unencrypted files
        # TODO: append endswith() clauses to check for
        # ".png", ".jpeg" and other image file formats
        for file in os.listdir(img_dir):
            filename = os.fsdecode(file)
            if filename.endswith(
                    ".jpg") and not filename.startswith("encrypted"):
                os.remove("media/images/" + filename)

        # TODO: File is "Untitled" now on front end,
        # send original image title along with other meta data
        # about image to be rendered on frontend
        return JsonResponse(image_filenames, safe=False)
