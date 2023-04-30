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
    # List all of the wishlists and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/wishlists"
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
