import django_filters

from apps.products.models import Product

class ProductFilter(django_filters.FilterSet):
    min_price    = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price    = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category     = django_filters.CharFilter(field_name="category__slug")
    shop         = django_filters.CharFilter(field_name="shop__slug")
    in_stock     = django_filters.BooleanFilter(method="filter_in_stock")
    has_discount = django_filters.BooleanFilter(method="filter_has_discount")
    class Meta:
        model  = Product
        fields = ["category", "shop", "is_available"]
    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset
    def filter_has_discount(self, queryset, name, value):
        return queryset.filter(old_price__isnull=False) if value else queryset

