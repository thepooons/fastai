# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/09b_vision.utils.ipynb (unless otherwise specified).

__all__ = ['download_images', 'resize_to', 'verify_image', 'verify_images', 'resize_image', 'resize_images']

# Cell
from ..torch_basics import *
from ..data.all import *
from .core import *

# Cell
def _download_image_inner(dest, inp, timeout=4):
    i,url = inp
    suffix = re.findall(r'\.\w+?(?=(?:\?|$))', url)
    suffix = suffix[0] if len(suffix)>0  else '.jpg'
    try: download_url(url, dest/f"{i:08d}{suffix}", overwrite=True, show_progress=False, timeout=timeout)
    except Exception as e: f"Couldn't download {url}."

# Cell
def download_images(dest, url_file=None, urls=None, max_pics=1000, n_workers=8, timeout=4):
    "Download images listed in text file `url_file` to path `dest`, at most `max_pics`"
    if urls is None: urls = url_file.read().strip().split("\n")[:max_pics]
    dest = Path(dest)
    dest.mkdir(exist_ok=True)
    parallel(partial(_download_image_inner, dest, timeout=timeout), list(enumerate(urls)), n_workers=n_workers)

# Cell
def resize_to(img, targ_sz, use_min=False):
    "Size to resize to, to hit `targ_sz` at same aspect ratio, in PIL coords (i.e w*h)"
    w,h = img.size
    min_sz = (min if use_min else max)(w,h)
    ratio = targ_sz/min_sz
    return int(w*ratio),int(h*ratio)

# Cell
def verify_image(fn):
    "Confirm that `fn` can be opened"
    try:
        im = Image.open(fn)
        im.draft(im.mode, (32,32))
        im.load()
        return True
    except: return False

# Cell
def verify_images(fns):
    "Find images in `fns` that can't be opened"
    return L(fns[i] for i,o in enumerate(parallel(verify_image, fns)) if not o)

# Cell
def resize_image(file, dest, max_size=None, n_channels=3, ext=None,
                 img_format=None, resample=Image.BILINEAR, resume=False, **kwargs ):
    "Resize file to dest to max_size"
    dest = Path(dest)
    dest_fname = dest/file.name
    if resume and dest_fname.exists(): return
    if verify_image(file):
        img = Image.open(file)
        imgarr = np.array(img)
        img_channels = 1 if len(imgarr.shape) == 2 else imgarr.shape[2]
        if (max_size is not None and (img.height > max_size or img.width > max_size)) or img_channels != n_channels:
            if ext is not None: dest_fname=dest_fname.with_suffix(ext)
            if max_size is not None:
                new_sz = resize_to(img, max_size)
                img = img.resize(new_sz, resample=resample)
            if n_channels == 3: img = img.convert("RGB")
            img.save(dest_fname, img_format, **kwargs)

# Cell
def resize_images(path, max_workers=defaults.cpus, max_size=None, recurse=False,
                  dest=Path('.'), n_channels=3, ext=None, img_format=None, resample=Image.BILINEAR,
                  resume=None, **kwargs):
    "Resize files on path recursively to dest to max_size"
    path = Path(path)
    if resume is None and dest != Path('.'): resume=False
    os.makedirs(dest, exist_ok=True)
    files = get_image_files(path, recurse=recurse)
    parallel(resize_image, files, max_workers=max_workers, max_size=max_size, dest=dest, n_channels=n_channels, ext=ext,
                   img_format=img_format, resample=resample, resume=resume, **kwargs)