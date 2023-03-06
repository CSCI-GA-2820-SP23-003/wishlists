"""
Test cases for Items Models
Test cases can be run with:
    nosetests
    coverage report -m
While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_items_model.py:TestItemsModel
"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Wishlists,Items, DataValidationError, db
from service import app
from tests.factories import ItemsFactory, WishlistsFactory
import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  ITEMS   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestItemsModel(unittest.TestCase):
    """Test Cases for Items Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Items.init_db(app)
        Wishlists.init_db(app)


    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Items).delete()  # clean up the last tests
        db.session.query(Wishlists).delete()  # clean up the wishlists
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_item(self):
        """It should Create an item and assert that it exists"""
        item = Items(product_name="first item", wishlist_id=1, item_quantity=1)
        self.assertEqual(str(item), "<Item first item id=[None]>")
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, None)
        self.assertEqual(item.product_name, "first item")
        self.assertEqual(item.wishlist_id, 1)
        self.assertEqual(item.item_quantity, 1)

    # def test_add_an_item(self):
    #     """It should Create an item and add it to the database"""
    #     wish = Wishlists.all()
    #     self.assertEqual(wish, [])
    #     items = Items.all()
        
    #     self.assertEqual(items, [])
    #     # current_time = datetime.datetime.now()
    #     wishlist = WishlistsFactory()
    #     wishlist.wishlist_id=None
    #     wishlist.create()
    #     item = Items(product_name="first item", wishlist_id=1, item_quantity=1)
    #     self.assertTrue(item is not None)
    #     self.assertEqual(item.item_id, None)
    #     item.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(item.item_id)
    #     items = Items.all()
    #     self.assertEqual(len(items), 1)

    # def test_read_a_item(self):
    #     """It should Read a item"""
    #     wishlist = WishlistsFactory()
    #     wishlist.wishlist_id = None
    #     wishlist.create()
    #     item = ItemsFactory()
    #     logging.debug(item)
    #     item.item_id = None
    #     item.wishlist_id = wishlist.wishlist_id
    #     item.create()
    #     self.assertIsNotNone(item.item_id)
    #     # Fetch it back
    #     found_item = Items.find(item.item_id)
    #     self.assertEqual(found_item.item_id, item.item_id)
    #     self.assertEqual(found_item.product_name, item.product_name)
    #     self.assertEqual(found_item.wishlist_id, item.wishlist_id)
    #     self.assertEqual(found_item.product_id, item.product_id)
    #     self.assertEqual(found_item.item_quantity, item.item_quantity)
