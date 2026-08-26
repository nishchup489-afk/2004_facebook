import cloudinary.uploader

from app.config import media


result = cloudinary.uploader.upload(
    "tests/test.webp",
    folder="thefacebook/test",
)


print(result["secure_url"])