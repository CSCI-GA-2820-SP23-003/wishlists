"""
Wishlist Steps
Steps file for Wishlist.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following wishlists')
def step_impl(context):
    """ Delete all Wishlists and load new ones """
    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/wishlists"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{wishlist['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new wishlists
    for row in context.table:
        payload = {
            "name": row['name'],
            "owner_id": int(row['owner_id']),
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)


@given('the following wishlist items')
def step_impl(context):
    """ Delete all existing wishlist items and load new ones """
    # List all of the wishlist items and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/wishlists"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        wishlist_id = wishlist['id']
        clear_endpoint = f"{context.BASE_URL}/wishlists/{wishlist_id}/clear"
        context.resp = requests.put(clear_endpoint)
        expect(context.resp.status_code).to_equal(200)

    # Load the database with new wishlist items
    for row in context.table:
        wishlist_name = row['wishlist_name']
        query = 'name=' + wishlist_name
        rest_endpoint = f"{context.BASE_URL}/wishlists?{query}"
        context.resp = requests.get(rest_endpoint)
        wishlist_id = context.resp.json()[0]['id']
        payload = {
            "wishlist_id": wishlist_id,
            "product_name": row['name'],
            "product_id": int(row['product_id']),
            "item_quantity": int(row['quantity']),
            "id": None
        }
        endpoint = f"{context.BASE_URL}/wishlists/{wishlist_id}/items"
        context.resp = requests.post(endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
