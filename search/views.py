from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from mongoengine.queryset.visitor import Q as MongoQ
from .models import SearchHistory, PopularSearch
from .serializers import (
    SearchHistorySerializer, PopularSearchSerializer,
    UnifiedSearchResultSerializer
)
from book.models import Book
from mobile.models import Mobile
from shoes.models import Shoes

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Unified search across all product types with filtering and sorting.
        """
        query = request.query_params.get('q', '').strip()
        product_type = request.query_params.get('type')  # book, mobile, shoes
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort_by', 'relevance')  # relevance, price_asc, price_desc
        in_stock = request.query_params.get('in_stock', 'false').lower() == 'true'

        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Track search query
        if len(query) >= 3:  # Only track meaningful searches
            PopularSearch.increment_search(query)

        # Prepare price filters
        price_filter = MongoQ()
        if min_price:
            try:
                price_filter &= MongoQ(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                price_filter &= MongoQ(price__lte=float(max_price))
            except ValueError:
                pass

        # Stock filter
        stock_filter = MongoQ(stock__gt=0) if in_stock else MongoQ()

        # Search in each product type
        results = []

        if not product_type or product_type == 'book':
            book_results = self._search_books(query, price_filter, stock_filter)
            results.extend(book_results)

        if not product_type or product_type == 'mobile':
            mobile_results = self._search_mobiles(query, price_filter, stock_filter)
            results.extend(mobile_results)

        if not product_type or product_type == 'shoes':
            shoes_results = self._search_shoes(query, price_filter, stock_filter)
            results.extend(shoes_results)

        # Sort results
        if sort_by == 'price_asc':
            results.sort(key=lambda x: float(x.price))
        elif sort_by == 'price_desc':
            results.sort(key=lambda x: float(x.price), reverse=True)
        # For relevance, results are already sorted by the individual searches

        # Save search history
        SearchHistory.objects.create(
            user=request.user,
            query=query,
            filters={
                'type': product_type,
                'min_price': min_price,
                'max_price': max_price,
                'sort_by': sort_by,
                'in_stock': in_stock
            },
            results_count=len(results)
        )

        # Serialize results
        serializer = UnifiedSearchResultSerializer(results, many=True)
        return Response({
            'query': query,
            'total_results': len(results),
            'results': serializer.data
        })

    def _search_books(self, query, price_filter, stock_filter):
        return Book.objects.filter(
            (MongoQ(title__icontains=query) |
             MongoQ(author__icontains=query) |
             MongoQ(description__icontains=query)) &
            price_filter & stock_filter
        )

    def _search_mobiles(self, query, price_filter, stock_filter):
        return Mobile.objects.filter(
            (MongoQ(name__icontains=query) |
             MongoQ(brand__icontains=query) |
             MongoQ(description__icontains=query) |
             MongoQ(processor__icontains=query)) &
            price_filter & stock_filter
        )

    def _search_shoes(self, query, price_filter, stock_filter):
        return Shoes.objects.filter(
            (MongoQ(name__icontains=query) |
             MongoQ(brand__icontains=query) |
             MongoQ(description__icontains=query) |
             MongoQ(category__icontains=query)) &
            price_filter & stock_filter
        )

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's search history."""
        history = SearchHistory.objects.filter(user=request.user)
        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular search queries."""
        popular = PopularSearch.objects.all()[:10]  # Top 10 searches
        serializer = PopularSearchSerializer(popular, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions based on partial query."""
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response([])

        # Get suggestions from each product type
        suggestions = set()

        # Book suggestions
        book_suggestions = Book.objects.filter(
            MongoQ(title__icontains=query) |
            MongoQ(author__icontains=query)
        ).limit(5)
        suggestions.update(book.title for book in book_suggestions)

        # Mobile suggestions
        mobile_suggestions = Mobile.objects.filter(
            MongoQ(name__icontains=query) |
            MongoQ(brand__icontains=query)
        ).limit(5)
        suggestions.update(mobile.name for mobile in mobile_suggestions)

        # Shoes suggestions
        shoes_suggestions = Shoes.objects.filter(
            MongoQ(name__icontains=query) |
            MongoQ(brand__icontains=query)
        ).limit(5)
        suggestions.update(shoes.name for shoes in shoes_suggestions)

        # Add popular searches that match the query
        popular_suggestions = PopularSearch.objects.filter(
            query__icontains=query
        ).values_list('query', flat=True)[:5]
        suggestions.update(popular_suggestions)

        return Response(sorted(list(suggestions))[:10])
