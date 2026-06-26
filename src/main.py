import os
import shutil


def copy_contents_recursive(src_dir: str, dest_dir: str) -> None:
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            os.mkdir(dest_path)
            copy_contents_recursive(src_path, dest_path)


def copy_static_to_public() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, "static")
    dest_dir = os.path.join(project_root, "public")

    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Static directory not found: {src_dir}")

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    os.mkdir(dest_dir)
    copy_contents_recursive(src_dir, dest_dir)


def main() -> None:
    copy_static_to_public()


if __name__ == "__main__":
    main()
