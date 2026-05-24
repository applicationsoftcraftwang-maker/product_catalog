
# AI Assistance Disclosure: This document was prepared with assistance from an AI tool based on my implementation and project decisions. I  reviewed, edited, and verified the content to ensure it accurately reflects the final solution.


# Trade Material Catalog

A Django application for browsing and filtering construction materials, tools, and prefab assemblies — the kind of catalog a trade contractor's purchasing or warehouse team would use day-to-day.

---

## Setup

```bash
git clone https://github.com/applicationsoftcraftwang-maker/product_catalog.git
cd product_catalog

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

> **Admin population note:** The `seed_data` command is provided for reviewer convenience. The same data can also be populated manually through the Django admin at `/admin/`, which is what the assignment requires — add Categories first, then Tags, then Products using the admin forms.

Create an admin login:

```bash
python manage.py createsuperuser
```

To wipe and re-seed from scratch:

```bash
python manage.py seed_data --clear
```

---

## Models

```
Category  ─────<  Product  >─────  Tag
(1)              (many)            (many)
```

- `Category → Product` is a ForeignKey with `on_delete=PROTECT` — prevents deleting a category while materials still reference it.
- `Product ↔ Tag` is ManyToMany — materials share tags freely across categories.
- `Product.status` is an explicit choice field: `available`, `low_stock`, or `backordered`. Set by the purchasing or warehouse team, not derived from stock count alone (a material can be backordered even if a few units remain).
- `Product.is_prefab_item` flags materials built in the warehouse before going to site.

---

## Search and Filter

The catalog supports four combinable filters:

- **Description search** — matches `name OR description` using `icontains`
- **Category** — exact FK filter
- **Availability status** — filters by `available`, `low_stock`, or `backordered`
- **Jobsite tags** — chained `.filter()` calls, one per tag, so AND semantics apply. A material must carry all selected tags to appear in results. Using `__in` instead would give OR behaviour, which isn't right when a user selects multiple tags.

Results paginate at 9 per page. The `query_replace` custom template tag rebuilds the query string on each pagination link so active filters are preserved when moving between pages.

---

## Design Notes

I used Django templates rather than a separate front-end framework because the assignment is focused on models, querysets, and views. Adding a JS build step would complicate the setup without improving the thing being evaluated.

I added a `seed_data` management command because it makes setup repeatable in one step and is easy to re-run with `--clear` during development. The command is idempotent — it skips rows that already exist so it's safe to re-run.

The `status` field (available / low stock / backordered) is relevant in a construction material context where procurement and warehouse teams actively manage availability outside of just counting units. Backordered items still need to appear in the catalog so crews know they're coming.

The `is_prefab_item` flag is small but meaningful — prefab assemblies are built in the warehouse and tracked differently from raw materials. Showing a "PREFAB" badge on the card makes that visible at a glance.

---

## Business Context

This project is implemented as a small construction material catalog, using sample data and terminology that reflects how trade contractors manage materials, tools, and warehouse stock. Categories cover electrical supplies, conduit, fasteners, tools, prefab kits, safety gear, and warehouse consumables. Tags reflect how field crews and purchasing teams actually search — things like `jobsite-ready`, `reorder-needed`, `prefab`, and `safety-critical`.

The core assignment requirements are unchanged — products, categories, tags, search, filter, admin, and README — but the domain is closer to how a contractor procurement or warehouse team would use a catalog like this in practice.

---

## AI Assistance Disclosure

I used AI tools as a support resource for reviewing README clarity, improving wording, and checking common Django implementation patterns. I customized the domain, sample data, model relationships, queryset logic, templates, and final implementation myself.

I understand the full implementation and can explain the model relationships, Django admin setup, combined search and filter query logic, template rendering, and seed data structure during the interview.

