"""
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Item, Wishlist
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistsFactory, ItemsFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/wishlists"
######################################################################
#  T E S T   C A S E S
######################################################################
######################################################################
#  T E S T   WISHLIST   S E R V I C E
######################################################################


class TestWishlistService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def __create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistsFactory()
            response = self.app.post(BASE_URL, json=test_wishlist.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test wishlist"
            )
            new_wishlist = response.get_json()
            test_wishlist.id = new_wishlist["id"]
            wishlists.append(test_wishlist)
        return wishlists

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)    

    def test_get_wishlist_not_found(self):
        """It should not Read a Wishlist thats not found"""
        response = self.app.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""

        test_wishlist = WishlistsFactory()
        logging.debug("Test Wishlist: %s", test_wishlist.serialize())
        response = self.app.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = response.get_json()
        self.assertEqual(new_wishlist["id"], 1)
        self.assertEqual(new_wishlist["name"], test_wishlist.name)
        self.assertEqual(new_wishlist["owner_id"], test_wishlist.owner_id)
    
    def test_create_wishlists_with_no_data(self):
        """It should not Create an Wishlist with missing data"""
        response = self.app.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlists_no_content_type(self):
        """It should not Create a Wishlist with no content type"""
        response = self.app.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_wishlists_bad_content_type(self):
        """It should not Create an Wishlist with incorrect content type"""
        response = self.app.post(
            BASE_URL, headers={"Content-Type": "application/octet-stream"}
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_list_wishlists(self):
        """ It should list all wishlists"""
        self.__create_wishlists(10)
        response = self.app.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 10)


######################################################################
#  T E S T   ITEMS   S E R V I C E
######################################################################
class TestItemService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def __create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistsFactory()
            response = self.app.post(BASE_URL, json=test_wishlist.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test wishlist"
            )
            new_wishlist = response.get_json()
            test_wishlist.id = new_wishlist["id"]
            wishlists.append(test_wishlist)
        return wishlists

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_item(self):
        """It should Add an item to a wishlist"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["item_quantity"], item.item_quantity)

    def test_add_item_no_wishlist(self):
        """It should not Create a item when wishlist can't be found"""
        wishlist_id = 5
        item = ItemsFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_items_list(self):
        """It should Get a list of Items"""
        wishlist = self.__create_wishlists(1)[0]
        item_list = ItemsFactory.create_batch(2)
        
        item_one_response = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[0].serialize(), content_type="application/json"
        )
        self.assertEqual(item_one_response.status_code, status.HTTP_201_CREATED)
        
        item_two_response = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[1].serialize(), content_type="application/json"
        )
        self.assertEqual(item_two_response.status_code, status.HTTP_201_CREATED)
        
        resp = self.app.get(f"{BASE_URL}/{wishlist.id}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
