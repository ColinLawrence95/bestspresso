# Bestpresso Backend
![logo](/static/images/cup.png)
## About Bestpresso

Bestpresso is an e-commerce platform for coffee lovers, offering a curated selection of premium coffee blends. The backend, built with Flask and PostgreSQL, powers the core functionality, including user authentication, product management, cart operations, and product ratings. It serves a paginated product list (9 products per page) with random local photos assigned once to each product for consistency across the frontend. I created Bestpresso as a learning expericance to dive into the world of e-commerce and digital marketplaces.

For more details, visit the Bestpresso Frontend Repository: https://github.com/ColinLawrence95/bestspresso-front-end

## Getting Started

- **Deployed App**: Bestpresso
- **Backend Repository**: flask-api-bestpresso-back-end
- **Planning Materials**: Trello Board

To run locally:

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/flask-api-bestpresso-back-end.git
   cd flask-api-bestpresso-back-end
   ```

2. Install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up environment variables (`.env`):

   ```
   POSTGRES_DATABASE=your_db
   POSTGRES_USERNAME=your_user
   POSTGRES_PASSWORD=your_password
   JWT_SECRET=your_secret
   ```

4. Run the app:

   ```bash
   python3 app.py
   ```

5. Access at `http://localhost:5000`.

## Attributions

- Unsplash: Coffee photos used during development (replaced with local images in production).
- PostgreSQL: Database hosting on Heroku.

## Technologies Used

- **Python**: Core language.
- **Flask**: Web framework for API endpoints.
- **PostgreSQL**: Database for users, products, carts, and ratings.
- **Psycopg2**: PostgreSQL adapter.
- **Flask-CORS**: Cross-origin support for Netlify frontend.
- **Gunicorn**: WSGI server for Heroku.
- **Heroku**: Deployment platform.

## Next Steps

- **Search Functionality**: Add product search by name or description.
- **Filtering**: Allow filtering by price, rating, or stock.
- **Caching**: Implement Redis for faster product list queries.
- **Admin Dashboard**: Create endpoints for managing products and users.
- **Order History**: Add a table and endpoints for tracking past orders.