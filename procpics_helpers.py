import os

def getext(filename):
  if not os.path.isfile(filename):
    return ""

  (basename, ext) = os.path.splitext(filename)

  return ext

def containsdir(path):
  if not os.path.isdir(path):
    return False

  for element in os.listdir(path):
    if os.path.isdir(element) and element != "__newfiles__":
      return True

  return False

def isvalidimage(path, permitted_ext=['jpg', 'jpeg', 'webp', 'png']):
  if not os.path.isfile(path):
    return False

  ext = getext(path)

  for ext_test in permitted_ext:
    if ext_test in ext:
      return True

  return False
