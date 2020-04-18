# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../components"))


# -- Project information -----------------------------------------------------

project = "FastAPI Prototype"
copyright = "2020, Josh Wilson"
author = "Josh Wilson"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.graphviz",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "autoapi.extension",
]
autosectionlabel_prefix_document = True
todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    # Toc options
    # 'collapse_navigation': True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    # "includehidden": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Configure the autoapi extension
components_to_document = ["shared", "commands", "api"]
autoapi_type = "python"
autoapi_dirs = [f"../../components/{component}" for component in components_to_document] + [
    "../../bin",
    "../../build",
]
autoapi_add_toctree_entry = False
autoapi_options = ["members", "undoc-members", "show-inheritance", "special-members"]

# Remove the module path prefix from names in the auto docs
add_module_names = False

# Register an avent handler for "autoapi-skip-member" so we can more precisely
# cull unwanted items from the docs.
def setup(app):
    app.connect("autoapi-skip-member", skip_member_if)


def skip_member_if(app, what, name, obj, skip, options):
    if name == "bin":
        return True
    return (
        name.endswith(".logger")
        or (name.startswith("commands") and name.endswith(".parse_args"))
        or (name.startswith("bin") and name.endswith(".main"))
        or "autoapiskip:" in obj.docstring
    ) or None
