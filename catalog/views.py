import logging

from django.views.generic import ListView
from django.db.models import Q, Prefetch

from .models import Product, Tag
from .forms import ProductFilterForm

logger = logging.getLogger('catalog')

# How many results fit on one page
ITEMS_PER_PAGE = 9


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related(Prefetch("tags", queryset=Tag.objects.order_by("name")))
        )

        form = ProductFilterForm(self.request.GET)
        if not form.is_valid():
            logger.warning("Filter form invalid: %s", form.errors)
            return qs

        active_filters = []

        query = form.cleaned_data.get("query")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
            active_filters.append(f"query={query!r}")

        category = form.cleaned_data.get("category")
        if category:
            qs = qs.filter(category=category)
            active_filters.append(f"category={category.name!r}")

        status = form.cleaned_data.get("status")
        if status:
            qs = qs.filter(status=status)
            active_filters.append(f"status={status!r}")

        # Chained .filter() per tag gives AND semantics — product must carry ALL
        # chosen tags. Using __in would give OR (match any tag), which isn't right.
        selected_tags = form.cleaned_data.get("tags")
        if selected_tags:
            for tag in selected_tags:
                qs = qs.filter(tags=tag)
            tag_names = [t.name for t in selected_tags]
            active_filters.append(f"tags={tag_names}")

        qs = qs.distinct()

        result_count = qs.count()
        page = self.request.GET.get("page", 1)

        if active_filters:
            logger.info(
                "Catalog search — filters: [%s] → %d result(s) (page %s)",
                ", ".join(active_filters),
                result_count,
                page,
            )
        else:
            logger.debug("Catalog load — no filters, %d total products (page %s)", result_count, page)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = ProductFilterForm(self.request.GET)
        is_valid = form.is_valid()

        selected_tags     = form.cleaned_data.get("tags", []) if is_valid else []
        selected_category = form.cleaned_data.get("category")  if is_valid else None
        raw_status        = form.cleaned_data.get("status")     if is_valid else None

        # Resolve status key to its display label ("low_stock" → "Low Stock")
        status_labels = dict(Product.STATUS_CHOICES)

        context["form"]                 = form
        context["selected_tags"]        = selected_tags
        context["selected_category"]    = selected_category
        context["selected_status_label"]= status_labels.get(raw_status) if raw_status else None
        context["total_results"]        = self.get_queryset().count()

        # Log pagination navigation
        page_obj = context.get("page_obj")
        if page_obj and page_obj.paginator.num_pages > 1:
            logger.debug(
                "Pagination — page %d of %d (%d total results)",
                page_obj.number,
                page_obj.paginator.num_pages,
                context["total_results"],
            )

        return context
