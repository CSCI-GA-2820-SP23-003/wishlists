# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps
Steps file for web interactions with Selenium
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging, requests
from behave import when, then, given
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


@given('the following wishlist items')
def step_impl(context):
    """ Delete all existing wishlist items and load new ones """
    # List all of the wishlist items and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/wishlists"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        wishlist_id = wishlist['id']
        clear_endpoint = f"{context.BASE_URL}/api/wishlists/{wishlist_id}/clear"
        context.resp = requests.put(clear_endpoint)
        expect(context.resp.status_code).to_equal(204)

    # Load the database with new wishlist items
    for row in context.table:
        wishlist_name = row['wishlist_name']
        query = 'name=' + wishlist_name
        rest_endpoint = f"{context.BASE_URL}/api/wishlists?{query}"
        context.resp = requests.get(rest_endpoint)
        wishlist_id = context.resp.json()[0]['id']
        payload = {
            "wishlist_id": wishlist_id,
            "product_name": row['name'],
            "product_id": int(row['product_id']),
            "item_quantity": int(row['quantity']),
            "id": None
        }
        endpoint = f"{context.BASE_URL}/api/wishlists/{wishlist_id}/items"
        context.resp = requests.post(endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.BASE_URL)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id =  element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id =  element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id =  element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id("search_results")
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@then('I should see "{name}" in the item results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_item_results"), name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the item results')
def step_impl(context, name):
    element = context.driver.find_element_by_id("search_item_results")
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    expect(found).to_be(True)


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
