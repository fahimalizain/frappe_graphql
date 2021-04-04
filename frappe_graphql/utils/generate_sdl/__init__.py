import os
import frappe

from .root import get_root_sdl
from .doctype import get_doctype_sdl

IGNORED_DOCTYPES = [
    "Installed Application",
    "Installed Applications",
]


def make_doctype_sdl_files(target_dir, app=None, modules=[], doctypes=[],
                           ignore_root_file=False, ignore_custom_fields=False):
    doctypes = get_doctypes(
        app=app,
        modules=modules,
        doctypes=doctypes
    )

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    def write_file(filename, contents):
        target_file = os.path.join(target_dir, f"{frappe.scrub(filename)}.graphql")
        with open(target_file, "w") as f:
            f.write(contents)

    if not ignore_root_file:
        write_file("root", get_root_sdl())

    for doctype in doctypes:
        if doctype in IGNORED_DOCTYPES:
            continue
        sdl = get_doctype_sdl(doctype, ignore_custom_fields)
        write_file(doctype, sdl)


def get_doctypes(app=None, modules=None, doctypes=[]):
    modules = list(modules or [])
    doctypes = list(doctypes or [])
    if app:
        if app not in frappe.get_installed_apps():
            raise Exception("App {} is not installed in this site".format(app))

        modules.extend([x.name for x in frappe.get_all(
            "Module Def",
            {"app_name": app}
        )])

    if modules:
        for module in modules:
            if not frappe.db.exists("Module Def", module):
                raise Exception("Invalid Module: " + module)

        doctypes.extend([x.name for x in frappe.get_all(
            "DocType",
            {"module": ["IN", modules]}
        )])

    if doctypes:
        for dt in doctypes:
            if not frappe.db.exists("DocType", dt):
                raise Exception("Invalid DocType: " + dt)
    else:
        doctypes = [x.name for x in frappe.get_all("DocType")]

    return doctypes
