"""
Test Factory to make fake objects for testing
"""
import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
from service.models import Wishlist, Item


class WishlistsFactory(factory.Factory):
    """Creates fake wishlists that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    owner_id = FuzzyChoice(choices=[1, 2, 3])
    created_at = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=datetime.timezone.utc))
    wishlist_items = []


class ItemsFactory(factory.Factory):
    """Creates fake items that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Item

    id = factory.Sequence(lambda n: n)
    wishlist_id = 1
    product_id = FuzzyChoice(choices=[1, 2, 3])
    item_quantity = FuzzyChoice(choices=[1, 2, 3])
    product_name = factory.Faker("name")
