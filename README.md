# Static Site Generator

A Python static site generator that converts Markdown files into HTML pages.

The generator parses inline and block-level Markdown, builds an HTML tree of `TextNode` and `HTMLNode` objects, copies static assets, and writes a complete site to the `public/` directory.

## Project structure

```
static_site_generator/
├── content/              # Markdown source files (mirrors public/ layout)
│   ├── index.md
│   ├── contact/index.md
│   └── blog/
│       ├── glorfindel/index.md
│       ├── tom/index.md
│       └── majesty/index.md
├── static/               # Static assets (CSS, images) copied to public/
│   ├── index.css
│   └── images/
├── public/               # Generated site output (gitignored)
├── template.html         # HTML shell with {{ Title }} and {{ Content }} placeholders
├── src/
│   ├── main.py           # Build pipeline: copy static + generate pages
│   ├── htmlnode.py       # HTML tree nodes
│   ├── textnode.py       # Markdown parsing and conversion
│   ├── test_htmlnode.py
│   └── test_textnode.py
├── main.sh               # Build site and start local dev server
└── test.sh               # Run unit tests
```

## Quick start

### Build the site

```bash
python3 src/main.py
```

This will:

1. Delete and recreate `public/`
2. Copy everything from `static/` into `public/`
3. Generate an HTML page for every `.md` file in `content/`, preserving directory structure

### Build and serve locally

```bash
chmod +x main.sh   # first time only
./main.sh
```

Then open [http://localhost:8888](http://localhost:8888) in your browser.

### Run tests

From the project root:

```bash
bash test.sh
# or
python3 -m unittest discover -s src -v
```

## How it works

### Build pipeline (`main.py`)

| Function | Description |
|---|---|
| `copy_contents_recursive` | Recursively copies files and subdirectories from a source directory to a destination directory. |
| `copy_static_to_public` | Deletes `public/`, recreates it, and copies all contents from `static/`. |
| `generate_page` | Reads a Markdown file and `template.html`, converts Markdown to HTML, injects title and content into the template, and writes the result to the destination path. |
| `generate_pages_recursive` | Crawls every entry in the content directory. For each `.md` file found, generates a matching `.html` file in `public/` using the same directory structure. |
| `main` | Runs `copy_static_to_public`, then `generate_pages_recursive` over `content/`. |

**Example mapping:**

| Source | Output |
|---|---|
| `content/index.md` | `public/index.html` |
| `content/blog/glorfindel/index.md` | `public/blog/glorfindel/index.html` |
| `content/contact/index.md` | `public/contact/index.html` |

### Adding a new page

1. Create a Markdown file under `content/`, e.g. `content/about/index.md`
2. Start the file with an h1 heading: `# About`
3. Run `python3 src/main.py`
4. The page appears at `public/about/index.html`

## `htmlnode.py`

| Symbol | Description |
|---|---|
| `HTMLNode` | Base class for HTML tree nodes. Stores `tag`, `value`, `children`, and `props`. |
| `HTMLNode.props_to_html()` | Builds an HTML attribute string from `props`. |
| `LeafNode` | An HTML element with no children (e.g. `<p>`, `<a>`, plain text). |
| `LeafNode.to_html()` | Renders a leaf node. Void elements like `<img>` render from `props` only. |
| `ParentNode` | An HTML element with child nodes (e.g. `<div>`, `<ul>`, `<blockquote>`). |
| `ParentNode.to_html()` | Renders a parent node by wrapping child HTML in opening and closing tags. |

## `textnode.py`

### Enums and classes

| Symbol | Description |
|---|---|
| `TextType` | Inline text kinds: `TEXT`, `BOLD`, `ITALIC`, `CODE`, `LINK`, `IMAGE`. |
| `BlockType` | Block kinds: `PARAGRAPH`, `HEADING`, `CODE`, `QUOTE`, `UNORDERED_LIST`, `ORDERED_LIST`. |
| `TextNode` | A piece of inline text with a type and optional URL for links and images. |

### Inline parsing

| Function | Description |
|---|---|
| `text_node_to_html_node` | Converts a `TextNode` into a `LeafNode` (`TEXT` → plain text, `BOLD` → `<b>`, etc.). |
| `split_nodes_delimiter` | Splits `TEXT` nodes on a delimiter (`**`, `_`, `` ` ``). Raises if a delimiter is unclosed. |
| `split_nodes_image` | Splits `TEXT` nodes on `![alt](url)` image syntax. |
| `split_nodes_link` | Splits `TEXT` nodes on `[label](url)` link syntax. |
| `extract_markdown_images` | Returns `(alt, url)` tuples for all images in a string. |
| `extract_markdown_links` | Returns `(label, url)` tuples for all links (skips image syntax). |
| `text_to_textnodes` | Parses inline Markdown into a list of `TextNode` objects. |

### Block parsing

| Function | Description |
|---|---|
| `markdown_to_blocks` | Splits a document into blocks using blank lines (`\n\n`) as separators. |
| `block_to_block_type` | Detects block type from content (heading, code fence, quote, list, or paragraph). |
| `extract_title` | Returns the h1 title from a Markdown document. Raises if none is found. |

### HTML generation

| Function | Description |
|---|---|
| `text_to_children` | Converts inline Markdown text into a list of HTML child nodes. |
| `heading_to_html_node` | Renders a heading block as `<h1>`–`<h6>`. |
| `code_to_html_node` | Renders a fenced code block as `<pre><code>` without inline parsing. |
| `quote_to_html_node` | Renders a blockquote as `<blockquote><p>`. |
| `unordered_list_to_html_node` | Renders an unordered list as `<ul><li>`. |
| `ordered_list_to_html_node` | Renders an ordered list as `<ol><li>`. |
| `paragraph_to_html_node` | Renders a paragraph as `<p>`. |
| `markdown_to_html_node` | Converts a full Markdown document into a `<div>` tree of HTML nodes. |

## Supported Markdown

**Inline:** bold (`**`), italic (`_`), code (`` ` ``), links (`[text](url)`), images (`![alt](url)`)

**Blocks:**

- Headings: `#` through `######` (must have a space after `#`)
- Code fences: `` ``` `` blocks (no inline parsing inside)
- Blockquotes: every line starts with `>`
- Unordered lists: every line starts with `- `
- Ordered lists: lines numbered `1. `, `2. `, … in order
- Paragraphs: everything else (single newlines become spaces)

## Site pages

| Page | URL (when served) |
|---|---|
| Home | `/` |
| Why Glorfindel is More Impressive than Legolas | `/blog/glorfindel/` |
| Why Tom Bombadil Was a Mistake | `/blog/tom/` |
| The Unparalleled Majesty of "The Lord of the Rings" | `/blog/majesty/` |
| Contact | `/contact/` |
