"""
Seed the database with trade contractor material and tool sample data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear
"""

import logging
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Tag, Product

logger = logging.getLogger('catalog')

"""
***AI Assistance Disclosure***
These seed-datasets are generated and prepared with assistance from an AI tool based on my
implementation and project decisions. I reviewed, edited, and verified the content to ensure it
accurately reflects the final solution.
"""

CATEGORIES = [
    {"name": "Electrical Materials",  "description": "Wire, cable, boxes, and panel supplies for electrical rough-in and finish work."},
    {"name": "Conduit & Raceways",    "description": "EMT, PVC, liquid-tight conduit and fittings for wire management."},
    {"name": "Fasteners & Hardware",  "description": "Bolts, anchors, strut, cable tray brackets, and labelling supplies."},
    {"name": "Tools & Equipment",     "description": "Cordless tools, benders, and jobsite equipment for field crews."},
    {"name": "Prefab Assemblies",     "description": "Pre-assembled lighting whips, panel feeds, and room-in-a-box kits built in the warehouse."},
    {"name": "Safety Supplies",       "description": "PPE, lockout/tagout kits, and gas detection for compliant jobsite operations."},
    {"name": "Warehouse Stock",       "description": "Consumables, labels, and admin materials managed from the warehouse."},
]

TAGS = [
    "jobsite-ready", "warehouse-stock", "low-voltage", "high-demand",
    "prefab", "reorder-needed", "field-request", "bulk-order",
    "supplier-managed", "safety-critical", "rough-in", "finish-work",
]

PRODUCTS = [
    # --- Electrical Materials ---
    {"name": "MC Cable 12/2 with Ground",
     "description": "Metal-clad armoured cable, 12/2 AWG with bare ground. 250-foot coil. Used for branch circuit wiring in commercial and light industrial applications. Suitable for dry, damp, or wet locations.",
     "price": "189.00", "stock": 40, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["rough-in", "high-demand", "warehouse-stock"]},
    {"name": "THHN Wire 10 AWG Black 500ft",
     "description": "Single-conductor THHN/THWN-2 wire, 10 AWG, black, 500-foot pull box. Rated 600V. Standard for conduit runs on 30A circuits. Pulled with wire lubricant on longer runs.",
     "price": "142.00", "stock": 25, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["rough-in", "bulk-order", "warehouse-stock"]},
    {"name": "Copper Ground Wire #6 AWG 250ft",
     "description": "Bare copper grounding conductor, #6 AWG, 250-foot coil. Used for equipment grounding, ground rings, and bonding. Stocked in warehouse for high-volume project pulls.",
     "price": "215.00", "stock": 18, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["rough-in", "warehouse-stock", "high-demand"]},
    {"name": "4x4 Steel Junction Box",
     "description": "Standard 4-inch square steel junction box, 1-1/2 inch deep, with 1/2 and 3/4 inch knockouts. Used at pull points and device locations throughout rough-in. Comes in boxes of 25.",
     "price": "68.00", "stock": 120, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["rough-in", "bulk-order", "high-demand"]},
    {"name": "Single Gang Device Box Plastic",
     "description": "Non-metallic single gang box for new-work installations. Adjustable bracket for 3/4-inch drywall depth. Sold in cases of 100. Common finish-work item.",
     "price": "54.00", "stock": 200, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["finish-work", "bulk-order", "high-demand"]},
    {"name": "Wire Pulling Lubricant 1 Gallon",
     "description": "Water-based pulling compound for THHN and other conductors in conduit. Non-staining and residue-free. One gallon covers approximately 1,000 feet of 3/4-inch conduit.",
     "price": "28.00", "stock": 3, "status": "low_stock", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["warehouse-stock", "reorder-needed"]},
    {"name": "Panel Label Kit 120-Circuit",
     "description": "Peel-and-stick circuit directory labels for 120-circuit panels. Includes blank and pre-printed common circuit labels. Compatible with most residential and commercial panel brands.",
     "price": "14.50", "stock": 55, "status": "available", "is_prefab_item": False,
     "category": "Electrical Materials", "tags": ["finish-work", "warehouse-stock"]},
    # --- Conduit & Raceways ---
    {"name": "EMT Conduit 3/4 Inch 10ft",
     "description": "Electrical metallic tubing, 3/4-inch trade size, 10-foot length. Steel with zinc-coated interior. The most common conduit size on commercial jobs. Bent with a hand bender or mechanical bender.",
     "price": "9.75", "stock": 300, "status": "available", "is_prefab_item": False,
     "category": "Conduit & Raceways", "tags": ["rough-in", "bulk-order", "high-demand", "warehouse-stock"]},
    {"name": "PVC Conduit 1 Inch 10ft",
     "description": "Schedule 40 PVC conduit, 1-inch trade size, 10-foot length. Used underground, in concrete, and in wet locations where EMT is not permitted. Joined with solvent cement.",
     "price": "7.20", "stock": 150, "status": "available", "is_prefab_item": False,
     "category": "Conduit & Raceways", "tags": ["rough-in", "bulk-order", "warehouse-stock"]},
    {"name": "Liquid-Tight Flexible Conduit 1/2 Inch 25ft",
     "description": "Liquid-tight flexible metal conduit (LFMC), 1/2-inch, 25-foot coil. Used for final connections to motors, HVAC units, and equipment where vibration or movement is expected.",
     "price": "34.00", "stock": 0, "status": "backordered", "is_prefab_item": False,
     "category": "Conduit & Raceways", "tags": ["rough-in", "field-request", "reorder-needed"]},
    {"name": "Cable Tray Bracket 12 Inch",
     "description": "Steel wall-mount bracket for 12-inch-wide cable tray. Adjustable arm, powder-coat finish. Rated 50 lb per bracket. Sold individually; installed in pairs typically 5 feet apart.",
     "price": "18.50", "stock": 60, "status": "available", "is_prefab_item": False,
     "category": "Conduit & Raceways", "tags": ["rough-in", "warehouse-stock"]},
    # --- Fasteners & Hardware ---
    {"name": "Hex Bolt Set 3/8-16 Assorted",
     "description": "Assortment of 3/8-16 zinc-plated hex bolts in 1, 1.5, 2, and 3-inch lengths. 100 pieces per box. Used for strut connections, panel mounting, and equipment anchoring.",
     "price": "22.00", "stock": 80, "status": "available", "is_prefab_item": False,
     "category": "Fasteners & Hardware", "tags": ["warehouse-stock", "bulk-order"]},
    {"name": "Powder-Actuated Fastener Kit",
     "description": "Powder-actuated tool cartridges and drive pins for fastening strut and anchors to concrete and steel. Includes 100 fasteners and 100 cartridges.",
     "price": "89.00", "stock": 12, "status": "available", "is_prefab_item": False,
     "category": "Fasteners & Hardware", "tags": ["rough-in", "jobsite-ready"]},
    {"name": "Warehouse Bin Label Set 500pc",
     "description": "Self-adhesive bin labels for warehouse shelf and rack organization. 500 labels in 4 sizes. Writable surface and barcode-compatible. Used during material receiving and kitting operations.",
     "price": "31.00", "stock": 25, "status": "available", "is_prefab_item": False,
     "category": "Fasteners & Hardware", "tags": ["warehouse-stock"]},
    # --- Tools & Equipment ---
    {"name": "Cordless Hammer Drill 20V Kit",
     "description": "20V brushless cordless hammer drill with 2 batteries, charger, and case. 600 in-lb torque, 2-speed gearbox, 1/2-inch chuck. Standard issue for field crews on commercial projects.",
     "price": "249.00", "stock": 8, "status": "available", "is_prefab_item": False,
     "category": "Tools & Equipment", "tags": ["jobsite-ready", "high-demand", "field-request"]},
    {"name": "Impact Driver Kit 18V",
     "description": "18V brushless impact driver, 1,825 in-lb torque, 3-speed settings. Includes 2 batteries, rapid charger, and belt clip. Used for driving screws and hex-head fasteners on device and panel installs.",
     "price": "199.00", "stock": 5, "status": "low_stock", "is_prefab_item": False,
     "category": "Tools & Equipment", "tags": ["jobsite-ready", "field-request", "reorder-needed"]},
    {"name": "Conduit Bender 3/4 Inch",
     "description": "Hand bender for 3/4-inch EMT conduit. Calibrated degree markings for stub-up, back-to-back, offset, and saddle bends. One per field crew — tracked as a returnable tool.",
     "price": "42.00", "stock": 14, "status": "available", "is_prefab_item": False,
     "category": "Tools & Equipment", "tags": ["jobsite-ready", "rough-in"]},
    {"name": "Jobsite Extension Cord 100ft 12AWG",
     "description": "100-foot 12 AWG SJTW outdoor extension cord, 15A, 125V. Lighted end indicates power. Stays flexible in cold weather. Standard on all jobsites; tracked per crew.",
     "price": "58.00", "stock": 20, "status": "available", "is_prefab_item": False,
     "category": "Tools & Equipment", "tags": ["jobsite-ready", "field-request"]},
    # --- Prefab Assemblies ---
    {"name": "Prefabricated Lighting Whip 6ft",
     "description": "Pre-made 6-foot fixture whip with 1/2-inch liquid-tight, 12/2 MC cable tail, and wire nuts. Built in the warehouse and kitted per floor for faster field installation.",
     "price": "24.00", "stock": 85, "status": "available", "is_prefab_item": True,
     "category": "Prefab Assemblies", "tags": ["prefab", "finish-work", "jobsite-ready"]},
    {"name": "Prefab Panel Feed Assembly 200A",
     "description": "Pre-assembled 200A panel feed: 4-inch EMT nipple, 3/0 THHN conductors cut to spec, lugs installed. Built per project drawings to reduce field labour at panel termination.",
     "price": "310.00", "stock": 6, "status": "available", "is_prefab_item": True,
     "category": "Prefab Assemblies", "tags": ["prefab", "rough-in", "supplier-managed"]},
    {"name": "Prefab Room-in-a-Box Kit",
     "description": "Warehouse-assembled kit for a standard hotel or multi-res room: all device boxes, wire, plates, and devices pre-counted and bagged by room. Reduces material waste and speeds field installation by ~40%.",
     "price": "185.00", "stock": 0, "status": "backordered", "is_prefab_item": True,
     "category": "Prefab Assemblies", "tags": ["prefab", "finish-work", "high-demand", "reorder-needed"]},
    # --- Safety Supplies ---
    {"name": "Hard Hat Class E Yellow",
     "description": "Class E (electrical) vented hard hat, ANSI/ISEA Z89.1 rated. 4-point suspension, ratchet adjustment. Mandatory on all active jobsites; issued per worker.",
     "price": "18.00", "stock": 35, "status": "available", "is_prefab_item": False,
     "category": "Safety Supplies", "tags": ["safety-critical", "jobsite-ready", "warehouse-stock"]},
    {"name": "Safety Glasses ANSI Z87.1",
     "description": "Clear-lens safety glasses, ANSI Z87.1+ rated for impact resistance. Anti-scratch and anti-fog coating. Sold in boxes of 12. Stocked in the warehouse for distribution at site check-in.",
     "price": "38.00", "stock": 90, "status": "available", "is_prefab_item": False,
     "category": "Safety Supplies", "tags": ["safety-critical", "jobsite-ready", "bulk-order", "warehouse-stock"]},
    {"name": "Lockout Tagout Kit 10-Lock",
     "description": "OSHA-compliant LOTO kit: 10 safety padlocks, 12 hasp devices, tags, and lockout bag. One kit per crew on all electrical work. Inspected and replenished before each project.",
     "price": "94.00", "stock": 4, "status": "low_stock", "is_prefab_item": False,
     "category": "Safety Supplies", "tags": ["safety-critical", "reorder-needed", "jobsite-ready"]},
]


class Command(BaseCommand):
    help = "Seed the database with trade contractor material and tool data. Re-runnable — skips existing rows."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Wipe existing catalog data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            deleted_products = Product.objects.count()
            deleted_tags     = Tag.objects.count()
            deleted_cats     = Category.objects.count()
            Product.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            logger.info(
                "seed_data --clear: removed %d products, %d tags, %d categories",
                deleted_products, deleted_tags, deleted_cats,
            )
            self.stdout.write(self.style.WARNING("Existing data cleared."))

        # --- Categories ---
        self.stdout.write("Creating categories...")
        category_map = {}
        cats_created = 0
        for data in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                name=data["name"], defaults={"description": data["description"]}
            )
            category_map[obj.name] = obj
            if created:
                cats_created += 1
                logger.debug("Category created: %s", obj.name)
            self.stdout.write(f"  {'[new]' if created else '[skip]'} {obj.name}")
        logger.info("Categories: %d created, %d already existed", cats_created, len(CATEGORIES) - cats_created)

        # --- Tags ---
        self.stdout.write("\nCreating tags...")
        tag_map = {}
        tags_created = 0
        for tag_name in TAGS:
            obj, created = Tag.objects.get_or_create(name=tag_name)
            tag_map[obj.name] = obj
            if created:
                tags_created += 1
                logger.debug("Tag created: %s", obj.name)
            self.stdout.write(f"  {'[new]' if created else '[skip]'} {obj.name}")
        logger.info("Tags: %d created, %d already existed", tags_created, len(TAGS) - tags_created)

        # --- Products ---
        self.stdout.write("\nCreating products...")
        products_created = 0
        for data in PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": Decimal(data["price"]),
                    "stock": data["stock"],
                    "status": data["status"],
                    "is_prefab_item": data["is_prefab_item"],
                    "category": category_map[data["category"]],
                },
            )
            if created:
                products_created += 1
                for tag_name in data["tags"]:
                    product.tags.add(tag_map[tag_name])
                logger.debug("Product created: %s (category=%s, status=%s)", product.name, data["category"], data["status"])
            self.stdout.write(f"  {'[new]' if created else '[skip]'} {product.name}")

        logger.info(
            "seed_data complete — %d categories, %d tags, %d products in DB (%d products created this run)",
            Category.objects.count(), Tag.objects.count(), Product.objects.count(), products_created,
        )
        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {Category.objects.count()} categories, "
            f"{Tag.objects.count()} tags, {Product.objects.count()} materials."
        ))
