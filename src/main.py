import os
import shutil

from textnode import extract_title, markdown_to_html_node


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


def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    html_content = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html_content)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page)


def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str) -> None:
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)

        if os.path.isfile(from_path):
            if from_path.endswith(".md"):
                dest_html_path = os.path.splitext(dest_path)[0] + ".html"
                generate_page(from_path, template_path, dest_html_path)
        else:
            generate_pages_recursive(from_path, template_path, dest_path)


def main() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(project_root, "template.html")
    content_dir = os.path.join(project_root, "content")
    public_dir = os.path.join(project_root, "public")

    copy_static_to_public()
    generate_pages_recursive(content_dir, template_path, public_dir)


if __name__ == "__main__":
    main()
