"""
Test cases for Wishlists Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_wishlists_model.py:TestWishlistsModel

"""
import os
import logging
import unittest
import datetime
from werkzeug.exceptions import NotFound
from service.models import Wishlist, DataValidationError, db
from service import app
from tests.factories import WishlistsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  WISHLISTS   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistsModel(unittest.TestCase):
    """Test Cases for Wishlist Model"""

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
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should Create a wishlist and assert that it exists"""
        create_time = datetime.datetime.now()
        wishlist = Wishlist(name="first wishlist", owner_id=1, created_at=create_time)
        self.assertEqual(str(wishlist), "<Wishlist first wishlist id=[None]>")
        self.assertTrue(wishlist is not None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "first wishlist")
        self.assertEqual(wishlist.owner_id, 1)
        self.assertEqual(wishlist.created_at, create_time)

    def test_add_a_wishlist(self):
        """It should Create a wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        current_time = datetime.datetime.now()
        wishlist = Wishlist(name="first wishlist", owner_id=1, created_at=current_time)
        self.assertTrue(wishlist is not None)
        self.assertEqual(wishlist.id, None)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        logging.info(wishlist.id)
        self.assertEqual(len(wishlists), 1)

    def test_read_a_wishlist(self):
        """It should Read a wishlist"""
        wishlist = WishlistsFactory()
        logging.debug(wishlist)
        wishlist.id = None
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        # Fetch it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.name, wishlist.name)
        self.assertEqual(found_wishlist.owner_id, wishlist.owner_id)
        self.assertEqual(found_wishlist.created_at, wishlist.created_at)

    def test_update_a_wishlist(self):
        """It should Update a wishlist"""
        wishlist = WishlistsFactory()
        logging.debug(wishlist)
        wishlist.id = None
        wishlist.create()
        logging.debug(wishlist)
        self.assertIsNotNone(wishlist.id)
        # Change it an save it
        wishlist.owner_id = 2
        original_id = wishlist.id
        wishlist.update()
        self.assertEqual(wishlist.id, original_id)
        self.assertEqual(wishlist.owner_id, 2)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].id, original_id)
        self.assertEqual(wishlists[0].owner_id, 2)

    def test_update_no_id(self):
        """It should not Update a wishlist with no id"""
        wishlist = WishlistsFactory()
        logging.debug(wishlist)
        wishlist.id = None
        self.assertRaises(DataValidationError, wishlist.update)

    def test_delete_a_wishlist(self):
        """It should Delete a wishlist"""
        wishlist = WishlistsFactory()
        wishlist.create()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_list_all_wishlists(self):
        """It should List all wishlists in the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        # Create 5 wishlists
        for _ in range(5):
            wishlist = WishlistsFactory()
            wishlist.create()
        # See if we get back 5 wishlists
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 5)

    def test_serialize_a_wishlist(self):
        """It should serialize a wishlist"""
        wishlist = WishlistsFactory()
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], wishlist.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], wishlist.name)
        self.assertIn("owner_id", data)
        self.assertEqual(data["owner_id"], wishlist.owner_id)
        self.assertIn("created_at", data)
        self.assertEqual(data["created_at"], wishlist.created_at)

    def test_deserialize_a_wishlist(self):
        """It should de-serialize a wishlist"""
        data = WishlistsFactory().serialize()
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, data["name"])
        self.assertEqual(wishlist.owner_id, data["owner_id"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a wishlist with missing data"""
        data = {"id": 1, "name": "Kitty"}
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_bad_owner_id(self):
        """It should not deserialize a bad owner_id attribute"""
        test_wishlist = WishlistsFactory()
        data = test_wishlist.serialize()
        data["owner_id"] = "1"
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_find_wishlist(self):
        """It should Find a Wishlist by ID"""
        wishlists = WishlistsFactory.create_batch(5)
        for wishlist in wishlists:
            wishlist.create()
        logging.debug(wishlists)
        # make sure they got saved
        self.assertEqual(len(Wishlist.all()), 5)
        # find the 2nd wishlist in the list
        wishlist = Wishlist.find(wishlists[1].id)
        self.assertIsNot(wishlist, None)
        self.assertEqual(wishlist.id, wishlists[1].id)
        self.assertEqual(wishlist.name, wishlists[1].name)
        self.assertEqual(wishlist.owner_id, wishlists[1].owner_id)
        self.assertEqual(wishlist.created_at, wishlists[1].created_at)

    def test_find_by_owner_id(self):
        """It should Find Wishlists by Owner ID"""
        wishlists = WishlistsFactory.create_batch(10)
        for wishlist in wishlists:
            wishlist.create()
        owner_id = wishlists[0].owner_id
        count = len([wishlist for wishlist in wishlists if wishlist.owner_id == owner_id])
        found = Wishlist.find_by_owner_id(owner_id)
        self.assertEqual(found.count(), count)
        for wishlist in found:
            self.assertEqual(wishlist.owner_id, owner_id)

    def test_find_by_name(self):
        """It should Find a Wishlist by Name"""
        wishlists = WishlistsFactory.create_batch(5)
        for wishlist in wishlists:
            wishlist.create()
        name = wishlists[0].name
        found = Wishlist.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].owner_id, wishlists[0].owner_id)
        self.assertEqual(found[0].created_at, wishlists[0].created_at)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        wishlists = WishlistsFactory.create_batch(3)
        for wishlist in wishlists:
            wishlist.create()

        wishlist = Wishlist.find_or_404(wishlists[1].id)
        self.assertIsNot(wishlist, None)
        self.assertEqual(wishlist.id, wishlists[1].id)
        self.assertEqual(wishlist.name, wishlists[1].name)
        self.assertEqual(wishlist.owner_id, wishlists[1].owner_id)
        self.assertEqual(wishlist.created_at, wishlists[1].created_at)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Wishlist.find_or_404, 0)
