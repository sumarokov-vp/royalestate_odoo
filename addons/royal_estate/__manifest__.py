{
    "name": "Royal Estate",
    "version": "19.0.1.0.0",
    "category": "Real Estate",
    "summary": "Manage real estate properties",
    "description": """
        Royal Estate module for managing real estate properties.
    """,
    "author": "Royal Estate Team",
    "website": "",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
