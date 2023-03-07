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
from service.models import Wishlist, Item, DataValidationError, db
from service import app
from tests.factories import ItemsFactory, WishlistsFactory

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

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Item).delete()  # clean up the last tests
        db.session.query(Wishlist).delete()  # clean up the wishlists
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_item(self):
        """Creates an Item and asserts that it exist."""
        item = Item(product_name="first item", wishlist_id=1, item_quantity=1)
        self.assertEqual(str(item), "<Item first item id=[None]>")
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, None)
        self.assertEqual(item.product_name, "first item")
        self.assertEqual(item.wishlist_id, 1)
        self.assertEqual(item.item_quantity, 1)

    def test_add_item(self):
        """Creates an Item and adds it to the database."""

        wish = Wishlist.all()
        self.assertEqual(wish, [])
        items = Item.all()
        self.assertEqual(items, [])
        # Create a wishlist.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        # Create an item, and link it to the wishlist created above.
        item = Item(product_name="first item",
                     product_id=3,
                     wishlist_id=wishlist.wishlist_id,
                     item_quantity=1)
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, None)
        item.create()
        # Check that its assigned an id, and is present in our database.
        self.assertIsNotNone(item.item_id)
        items = Item.all()
        self.assertEqual(len(items), 1)

    def test_read_item(self):
        """Reads an Item from the database."""

        # Create a wishlist and add an Item to it.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        item = ItemsFactory()
        item.item_id, item.wishlist_id = None, wishlist.wishlist_id
        item.create()
        self.assertIsNotNone(item.item_id)

        # Read created item from the database, and verify that it has correct fields.
        fetch_item = Item.find(item.item_id)
        self.assertEqual(fetch_item.item_id, item.item_id)
        self.assertEqual(fetch_item.product_name, item.product_name)
        self.assertEqual(fetch_item.wishlist_id, item.wishlist_id)
        self.assertEqual(fetch_item.product_id, item.product_id)
        self.assertEqual(fetch_item.item_quantity, item.item_quantity)

    def test_update_item(self):
        """Updates an Item in the Database"""

        # Create a wishlist and a specific product.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        item = ItemsFactory()
        item.item_id, item.wishlist_id, item.product_id = None, wishlist.wishlist_id, 5
        item.create()
        logging.debug("Original Item: %s", item)

        # Making sure item exists.
        self.assertIsNotNone(item.item_id)

        # Changing product_id, product_name and quantity
        # Storing original item information
        original_item_id = item.item_id
        original_product_id, original_item_quantity = item.product_id, item.item_quantity
        # Modifying item information
        item.product_id = original_product_id+10
        item.product_name = "Modified Product"
        item.item_quantity = original_item_quantity+10
        # Update item
        item.update()
        logging.debug("Modified Item: %s", item)

        # 1.Make sure item primary key has not changed
        self.assertEqual(item.item_id, original_item_id)

        # 2. Make sure fields are updated.
        self.assertEqual(item.product_id, original_product_id+10)
        self.assertEqual(item.product_name, "Modified Product")
        self.assertEqual(item.item_quantity, original_item_quantity+10)

        # 3. Fetch once more from DB and ensure fields are modified
        items_from_db = Item.all()
        self.assertEqual(len(items_from_db), 1)
        test_item = items_from_db[0]
        self.assertEqual(test_item.product_id, original_product_id+10)
        self.assertEqual(test_item.product_name, "Modified Product")
        self.assertEqual(test_item.item_quantity, original_item_quantity+10)

    def test_delete_item(self):
        """Deletes an Item in the Database."""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        item = ItemsFactory()
        item.wishlist_id = wishlist.wishlist_id
        item.item_id = None
        item.create()

        # Ensure there's a valid item ID
        self.assertIsNotNone(item.item_id)

        # Ensure there is one item in the database.
        items_from_db = Item.all()
        self.assertEqual(len(items_from_db), 1)

        # Delete the item
        item.delete()

        # Fetch items again and ensure there are no items.
        items_from_db_post_delete = Item.all()
        self.assertEqual(len(items_from_db_post_delete), 0)

    def test_update_no_id(self):
        """It should not Update a item without an id"""
        # Create a Wishlist and an Item
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        item = ItemsFactory()
        item.item_id = None
        item.wishlist_id = wishlist.wishlist_id

        # Try updating the Item
        self.assertRaises(DataValidationError, item.update)

    def test_list_all_items(self):
        """Lists all Items in the Database"""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()

        # Create 5 items
        for _ in range(5):
            item = ItemsFactory()
            item.item_id = None
            item.wishlist_id = wishlist.wishlist_id
            item.create()

        # Check if we have 5 items in the DB
        items_from_db = Item.all()
        self.assertEqual(len(items_from_db), 5)

    def test_serialize_item(self):
        """Tests Item serialization"""

        item = ItemsFactory()
        serialized_data = item.serialize()

        # Ensure data has contents.
        self.assertNotEqual(serialized_data, None)

        # Ensure item has item-id
        self.assertIn("item_id", serialized_data)
        self.assertEqual(serialized_data["item_id"], item.item_id)

        # Ensure item has product_id
        self.assertIn("product_id", serialized_data)
        self.assertEqual(serialized_data["product_id"], item.product_id)

        # Ensure item has product name
        self.assertIn("product_name", serialized_data)
        self.assertEqual(serialized_data["product_name"], item.product_name)

        # Ensure item has wishlist_id
        self.assertIn("wishlist_id", serialized_data)
        self.assertEqual(serialized_data["wishlist_id"], item.wishlist_id)

        # Ensure item has quantity
        self.assertIn("item_quantity", serialized_data)
        self.assertEqual(serialized_data["item_quantity"], item.item_quantity)

    def test_deserialize_item(self):
        """Tests Item deserialization"""

        # Create a wishlist, and an Item in the Wishlist.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        item = ItemsFactory()
        item.item_id = None
        item.wishlist_id = wishlist.wishlist_id

        # data contains serialized dict
        data = item.serialize()

        # Transfer dict info to items object
        item = Item()
        item.deserialize(data)

        # Check if items object has valid data.
        # 1. Does it contain data
        self.assertNotEqual(item, None)
        self.assertEqual(item.item_id, None)

        # 2. Check if contents are correct.
        self.assertEqual(data["wishlist_id"], item.wishlist_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["item_quantity"], item.item_quantity)

    def test_deserialize_missing_data(self):
        """It should not deserialize a item with missing data"""

        # Create dict without product ID
        data = {"item_id": 1, "product_name": "item-1"}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""

        # Create a string variable and try to deserialize it
        data = "this is not a dictionary"
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_wishlist_id(self):
        """It should not deserialize a bad customer_id attribute"""

        # Create an Item in the Wishlist.
        test_item = ItemsFactory()

        # Serialize the item and put wishlist ID as string
        data = test_item.serialize()
        data["wishlist_id"] = "1"
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_product_id(self):
        """It should not deserialize a bad customer_id attribute"""

        # Create a wishlist, and an Item in the Wishlist.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        test_item = ItemsFactory()

        # Serialize the item and put product id as string
        data = test_item.serialize()
        data["product_id"] = "1"
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_item_quantity(self):
        """It should not deserialize a bad customer_id attribute"""

        # Create a wishlist, and an Item in the Wishlist.
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        test_item = ItemsFactory()

        # Serialize the item and put item_quantity as string
        data = test_item.serialize()
        data["item_quantity"] = "1"
        item = Item()

        # Check if correct Error is raised
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_find_item(self):
        """It should Find an item by ID"""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()

        # Add 5 Items in a wishlist
        items = ItemsFactory.create_batch(5)
        for item in items:
            item.wishlist_id = wishlist.wishlist_id
            item.create()
        logging.debug(items)

        # Make sure they got saved
        self.assertEqual(len(Item.all()), 5)

        # Find the 2nd item in the list and compare its attributes
        item = Item.find(items[1].item_id)
        self.assertIsNot(item, None)
        self.assertEqual(item.item_id, items[1].item_id)
        self.assertEqual(item.product_name, items[1].product_name)
        self.assertEqual(items[1].product_id, item.product_id)
        self.assertEqual(items[1].wishlist_id, item.wishlist_id)
        self.assertEqual(items[1].item_quantity, item.item_quantity)

    def test_find_by_wishlist_id(self):
        """It should Find items by wishlist id"""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()

        # Add 10 Items in a wishlist
        items = ItemsFactory.create_batch(10)
        for item in items:
            item.wishlist_id = wishlist.wishlist_id
            item.create()

        # Select a wishlist_id to search for
        wishlist_id = items[0].wishlist_id

        # Count the number of items in that selected wishlist
        count = len([item for item in items if item.wishlist_id == wishlist_id])

        # Filter the items from the database with specific wishlist_id
        found = Item.find_by_wishlist_id(wishlist_id)

        # Compare if both counts match
        self.assertEqual(found.count(), count)
        for item in found:
            self.assertEqual(item.wishlist_id, wishlist_id)

    def test_find_by_name(self):
        """It should Find an item by Name"""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()

        # Add 5 Items in a wishlist
        items = ItemsFactory.create_batch(5)
        for item in items:
            item.wishlist_id = wishlist.wishlist_id
            item.create()

        # Select a product name to search for
        name = items[0].product_name

        # Search for an item by "name" product_name
        found = Item.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].wishlist_id, items[0].wishlist_id)
        self.assertEqual(items[0].product_id, found[0].product_id)
        self.assertEqual(items[0].wishlist_id, found[0].wishlist_id)
        self.assertEqual(items[0].item_quantity, found[0].item_quantity)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        wishlist = WishlistsFactory()
        wishlist.wishlist_id = None
        wishlist.create()
        items = ItemsFactory.create_batch(3)
        for item in items:
            item.wishlist_id = wishlist.wishlist_id
            item.create()

        item = Item.find_or_404(items[1].item_id)
        self.assertIsNot(item, None)
        self.assertEqual(item.item_id, items[1].item_id)
        self.assertEqual(item.product_name, items[1].product_name)
        self.assertEqual(items[1].product_id, item.product_id)
        self.assertEqual(items[1].wishlist_id, item.wishlist_id)
        self.assertEqual(items[1].item_quantity, item.item_quantity)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Item.find_or_404, 0)
