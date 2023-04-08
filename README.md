# Cinema Site
This is a web application for a cinema site developed using Django. The site allows both admin and regular users to perform various actions related to movie screenings and ticket booking.

## Features
### User Authentication
Users can create accounts, log in, and log out of the site. Upon logging in, regular users will be automatically logged out after 1 minute of inactivity.

### Roles
There are two roles in the system: admin and regular user.

### Admin Actions
Admins can perform the following actions:

* Create cinema halls with names and sizes.
* Create screenings with start time, end time, date range, ticket prices, and hall.
* Modify halls and screenings as long as there are no tickets sold for that hall or screening.
* View all screenings and halls.
### User Actions
Regular users can perform the following actions:

* View a list of movie screenings for today or tomorrow.
* See the number of available seats in each hall.
* Purchase one or more tickets for a screening, receive a notification if the hall is sold out.
* View a list of all their purchases and the total amount spent.
* Sort screenings by ticket price or start time.  

Unauthenticated users can view the list of screenings but cannot make any purchases.

### REST API
All actions performed by both admins and users have corresponding REST API endpoints. These endpoints can be accessed using Postman or similar tools.

### Additional Features
* Screenings in the same hall cannot overlap.
* Screenings can be filtered by start time or hall using the REST API.
## Getting Started
To run the application, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies using pip install -r requirements.txt.
3. Create a .env file with the required environment variables.
4. Run python manage.py migrate to create the database tables.
5. Create a superuser account using python manage.py createsuperuser.
6. Run python manage.py runserver to start the development server.
7. Navigate to http://localhost:8000 in your web browser.
## Technologies Used
* Django
* Django REST framework
* SQLite
* HTML
* CSS