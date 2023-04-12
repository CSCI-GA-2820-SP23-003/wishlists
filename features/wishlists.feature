Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and items in them

Background:
    Given the following wishlists
        | name              | owner_id  |
        | Gift Ideas        | 3         |
        | Dream Items       | 4         |
        | Shopping List     | 3         |
        | Save for Later    | 5         |

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
    # When I paste the "Wishlist Id" field
    # And I press the "Retrieve" button
    # Then I should see the message "Success"
    # And I should see "wish_5" in the "Wishlist Name" field
    # And I should see "6" in the "Owner ID" field
