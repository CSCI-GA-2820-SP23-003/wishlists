"""
Test Factory to make fake objects for testing
"""
import datetime

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
from service.models import Wishlists


class WishlistsFactory(factory.Factory):
    """Creates fake wishlists that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlists

    wishlist_id = factory.Sequence(lambda n: n)
    wishlist_name = factory.Faker("name")
    owner_id = FuzzyChoice(choices=[1,2,3])
    created_at = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=datetime.timezone.utc))
