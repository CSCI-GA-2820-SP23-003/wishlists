Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and items in them

Background:
    Given the following wishlists
        | name              | owner_id  |
        | Gift Ideas        | 3         |
        | Watch List        | 4         |
        | Shopping List     | 3         |
        | Save for Later    | 5         |

    Given the following wishlist items
        | name      | wishlist_name | product_id    | quantity  |
        | Watch     | Gift Ideas    | 3             | 5         |
        | Earphone  | Gift Ideas    | 4             | 2         |
        | Milk      | Shopping List | 5             | 3         |
        | Bag       | Watch List    | 6             | 1         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "wedding_wishlist"
    And I set the "Owner ID" to "6"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID" field
    And I press the "Clear" button
    Then the "Wishlist ID" field should be empty
    And the "Wishlist Name" field should be empty
    And the "Owner ID" field should be empty
    # # To-do : When implementing retrieve button

# # Scenarios for Wishlist Items

Scenario: Create a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist name" to "Save for later"
    And I set the "Product Name" to "Jeans"
    And I set the "Product Id" to "85"
    And I set the "Item Quantity" to "1"
    And I press the "Create-Item" button
    Then I should see the message "Success"
    When I copy the "Item Id" field
    And I press the "Clear" button
    Then the "Product Name" field should be empty
    And the "Product Id" field should be empty
    And the "Owner Id" field should be empty
    # To-do : Add implementation for retrieve
