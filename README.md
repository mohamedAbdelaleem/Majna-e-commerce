# Majna-e-commerce
A B2C e-commerce that enables Egyptian customers to buy brand-name products confidently from authorized distributors.

## Contets
- ### [Requirements](#requirements)
- ### [Data Models](#data-models)
## Requirements
- the system should allow users to proceed as customers or sellers.
- users can sign up/log in using their emails.
- for a customer to place orders the system should store these information:
    - his Egyptian phone number.
    - his pickup address(Governate, city, street, house or apartment number)
    - a payment method.

- for a seller to activate his account he should provide:
    - his Egyptian national ID.
    - his Egyptian phone number.
    - the brand name (the system should provide the seller with available brands on typing and the seller can enter a brand that does not exist in the list)
    - the authorization document.
    - A bank account to receive funds

- reviewers then review sellers' applications and accept or cancel them. If the brand provided does not exist, the reviewer should ask his supervisor to add the brand.
- supervisors add/remove reviewers to the system, assign sellers' applications to the reviewers, and add brands.
- managers add/remove supervisors, activate/deactivate sellers(if a seller sells a fake product to customers), and deal with third-party shipping companies.

###

- sellers should provide for each product these information: (title, category, sub-category, brand, album, description)
- customers can ask questions about products and sellers can reply to them.
- sellers can display specific questions and answers on the product page.
- verified purchasers can add reviews to the products.

### 

- customers can search for products using relevant words that may exists in products' titles, descriptions, brand name, or category.
- customers can filter products by price range,  brand name, or product availability
- customers can sort products by price(low-to-high or high-to-low), average customers reviews, or featured

## Data Models

User(id, email, password, phone_num, is_active, is_stuff, is_superuser)
Customer(user_id)
Distributor(user_id)

  

