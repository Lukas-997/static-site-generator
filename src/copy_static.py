import os
import shutil

def copy_static(src: str, dst: str):
    # Delete destination directory if it exists
    if os.path.exists(dst):
        shutil.rmtree(dst)

    # Recreate destination root
    os.mkdir(dst)

    def _copy_dir(src_dir, dst_dir):
        for name in os.listdir(src_dir):
            src_path = os.path.join(src_dir, name)
            dst_path = os.path.join(dst_dir, name)

            if os.path.isfile(src_path):
                print(f"Copying file: {src_path} -> {dst_path}")
                shutil.copy(src_path, dst_path)
            else:
                print(f"Creating directory: {dst_path}")
                os.mkdir(dst_path)
                _copy_dir(src_path, dst_path)

    _copy_dir(src, dst)
