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
    When I paste the "Wishlist ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "wedding_wishlist" in the "Wishlist Name" field
    And I should see "6" in the "Owner ID" field


Scenario: Search for Wishlist with wishlist name
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Gift Ideas" in the results
    And I should not see "Save for Later" in the results

Scenario: Search for Wishlist with given Owner ID
    When I visit the "Home Page"
    And I set the "Owner Id" to "3"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Gift Ideas" in the results
    And I should see "Shopping List" in the results
    And I should not see "Save for Later" in the results

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Gift Ideas" in the "Wishlist Name" field
    And I should see "3" in the "Owner Id" field
    When I change "Wishlist Name" to "Birthday Ideas"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id" field
    And I press the "Clear" button
    And I paste the "Wishlist Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Birthday Ideas" in the "Wishlist Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Birthday Ideas" in the results
    And I should not see "Gift Ideas" in the results

##----------------------------------- Scenarios for Wishlist Items ----------------------------------- 

Scenario: Create a Wishlist Item
    When I visit the "Home Page"
    And I set the "Owner Id" to "5"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id" field
    And I press the "Clear" button
    Then the "Wishlist Id" field should be empty
    And the "Wishlist Name" field should be empty
    And the "Owner Id" field should be empty
    When I paste the "Wishlist Id" field
    And I set the "Product Name" to "Jeans"
    And I set the "Product Id" to "9"
    And I set the "Item Quantity" to "5"
    And I press the "Create-Item" button
    Then I should see the message "Success"

Scenario: Search for Wishlist Item with given name
    When I visit the "Home Page"
    And I set the "Wishlist name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id" field
    And I press the "Clear" button
    When I paste the "Wishlist Id" field
    And I set the "Product Name" to "Watch"
    And I press the "Search-Item" button
    Then I should see the message "Success"
    And I should see "Watch" in the item results
    And I should not see "Earphone" in the item results
    And I should not see "Milk" in the item results

Scenario: Empty a Wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "3" in the "Owner Id" field
    When I press the "Empty" button
    Then I should see the message "Gift Ideas wishlist has been cleared!"
    When I press the "Search-Item" button
    Then I should see the message "Success"
    And I should not see "Earphone" in the item results


Scenario: Update a Wishlist Item
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id" field
    And I press the "Clear" button
    When I paste the "Wishlist Id" field
    And I set the "Product Name" to "Watch"
    And I press the "Search-Item" button
    Then I should see the message "Success" 
    And I should see "Watch" in the item results
    When I change "Product Name" to "Cellphone"
    And I press the "Update-Item" button
    Then I should see the message "Success"     
    When I set the "Wishlist Name" to "Gift Ideas"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id" field
    And I press the "Clear" button
    When I paste the "Wishlist Id" field
    And I press the "Search-Item" button
    Then I should see the message "Success"
    And I should see "Cellphone" in the item results
    And I should not see "Watch" in the item results