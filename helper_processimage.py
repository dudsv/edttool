import os
from PIL import Image as img

max_width = 1300
reduce_quality_for = 50
reduce_quality_for_1 = 70
reduce_quality_for_2 = 50
reduce_quality_for_3 = 30

def getext(filename):
  if not os.path.isfile(filename):
    return ""

  (basename, ext) = os.path.splitext(filename)

  return ext

def isvalidimage(path, permitted_ext=['jpg', 'jpeg', 'webp', 'png']):
  if not os.path.isfile(path):
    return False

  ext = getext(path)

  for ext_test in permitted_ext:
    if ext_test in ext:
      return True

  return False

def process_image(img_path: str):
  if not os.path.isfile(img_path):
    print(f"File not found. {img_path}?")
    return

  (basename, ext) = os.path.splitext(img_path)
  pic = img.open(img_path)
  file_to_create = f"{basename}-compressed{ext}"
  file_to_create_0 = f"{basename}-compressed-0.jpg"
  file_to_create_1 = f"{basename}-compressed-1.jpg"
  file_to_create_2 = f"{basename}-compressed-2.jpg"
  file_to_create_3 = f"{basename}-compressed-3.jpg"
  file_to_create_4 = f"{basename}-compressed-4{ext}"
  file_to_create_5 = f"{basename}-compressed-5{ext}"
  file_to_create_6 = f"{basename}-compressed-6{ext}"
  file_to_create_7 = f"{basename}-compressed-7{ext}"
  file_to_create_8 = f"{basename}-compressed-8{ext}"

  width, height = pic.size
  new_size_2 = (int(width * 0.9), int(height * 0.9))
  new_size_3 = (int(width * 0.8), int(height * 0.8))
  new_size_4 = (int(width * 0.7), int(height * 0.7))
  new_size_5 = (int(width * 0.6), int(height * 0.6))
  new_size_6 = (int(width * 0.5), int(height * 0.5))

  if width > max_width:
    new_size = (max_width, int(height / width * max_width))
    pic = pic.resize(new_size)
  elif ext == 'png':
    new_size = (int(width * 0.9), int(height * 0.9))
    pic = pic.resize(new_size)
  else:
    new_size = (width, height)

  # in case of transparent bg includes a white bg.
  if ext == 'png' and not pic.mode == 'RGB':
    pic_bg = img.new('RGB', new_size, (255, 255, 255))
    pic_bg.paste(pic, pic)
    pic = pic_bg

  try:
    # pic.save(file_to_create, quality=reduce_quality_for)
    pic.save(file_to_create_0)
    # pic.save(file_to_create_1, quality=reduce_quality_for_1)
    # pic.save(file_to_create_2, quality=reduce_quality_for_2)
    # pic.save(file_to_create_3, quality=reduce_quality_for_3)

    pic_cp = pic.resize(new_size_2)
    pic_cp.save(file_to_create_4, quality=reduce_quality_for_1)
    # pic_cp = pic.resize(new_size_3)
    # pic_cp.save(file_to_create_5, quality=reduce_quality_for_1)
    # pic_cp = pic.resize(new_size_4)
    # pic_cp.save(file_to_create_6, quality=reduce_quality_for_1)
    # pic_cp = pic.resize(new_size_5)
    # pic_cp.save(file_to_create_7, quality=reduce_quality_for_1)
    pic_cp = pic.resize(new_size_6)
    pic_cp.save(file_to_create_8, quality=reduce_quality_for_1)
  except Exception as e:
      print("Could not process image", e)
