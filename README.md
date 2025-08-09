# Shopping Website

This project is a simple shopping website built using Python Flask. It allows users to browse products categorized into four types: crystals, silver jewelry, rings, and earrings. The website features an admin interface for managing products, including adding, modifying, deleting, and querying product information.

## Project Structure

```
shopping-website
├── app.py                # Main entry point of the Flask application
├── admin                 # Admin module for managing products
│   ├── __init__.py      # Initializes the admin module
│   └── views.py         # Contains views for the admin site
├── products              # Products module for storing product data
│   ├── __init__.py      # Initializes the products module
│   └── data.py          # Stores product data without using a database
├── static
│   └── images           # Directory for storing product images
├── templates             # HTML templates for rendering pages
│   ├── base.html        # Base template for the website
│   ├── index.html       # Main shopping page
│   ├── product.html     # Detailed product page
│   ├── admin.html       # Admin management interface
│   └── admin_edit.html  # Admin edit product page
├── requirements.txt      # Lists project dependencies
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python app.py
   ```

5. Access the shopping website at `http://127.0.0.1:5000/`.

## Usage Guidelines

- Users can browse products on the main page and view details for each product.
- Admins can manage products through the admin interface, accessible at `http://127.0.0.1:5000/admin`.
- Admin functionalities include adding new products, editing existing products, deleting products, and uploading images.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements."# myshopping" 
