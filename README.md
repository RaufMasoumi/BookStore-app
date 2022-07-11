# BookStore
## _A big django book store web application_


![GitHub last commit](https://img.shields.io/github/last-commit/RaufMasoumi/BookStore-app?logo=github) ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/RaufMasoumi/BookStore-app?color=yellow&logo=python&logoColor=yellow) ![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/RaufMasoumi/BookStore-app/django?color=important&logo=django) ![Lines of code](https://img.shields.io/tokei/lines/github/RaufMasoumi/BookStore-app?color=success) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/RaufMasoumi/BookStore-app?color=orange)

BookStore is a big sample bookstore Django project that provides all the features you need to buy a book.

The nicknames that describe the BookStore:

- Powerful
- Easy-to-use
- Super dynamic

The project was deployed to Heroku and you can check it now at [rauf-book-store-app.herokuapp.com](https://rauf-book-store-app.herokuapp.com) (For the best experience please add this site to your browser's trusted sites list).

The first idea and the base of this project was written from [Django For Professionals](https://djangoforprofessionals.com/) book.

The base and non-dynamic template or actual front-end is from [KeenThemes.com](https://KeenThemes.com).


## Features


- Easily create an account with Google account
- Edit account information
- Reset account password if forgot it
- Create, update and delete addresses of account, no need to rewrite it each time
- Easily add books to cart
- Add books to wishlist if loved
- Write reviews to any books and rate it
- Every information about books to safe purchase
- Search any book or author easily
- Book Categories to see just related books
- Compare books easily


## Tech

BookStore to being a web application with high self-confidence uses:

- [Python](https://www.python.org/) - The popular programming language
- [Django](https://www.djangoproject.com/) - An awesome backend framework written with python
- [Postgresql](https://www.postgresql.org) - A powerful, open source object-relational database
- [Docker](https://www.docker.com/) - A technology for OS-level virtualization
- [Docker Compose](https://docs.docker.com/compose/) - A tool for defining and running multi-container Docker applications
- [Heroku](https://www.heroku.com/) - A cloud platform as a service
- [Cloudinary](https://cloudinary.com/) - A technology for uploading files
- Front-end technologies

By joining all of these technologies together in one project, BookStore now has a powerful django backend that uses all the python magics to be as dynamic as possible, the world's most advanced open source database, one of the most popular ways for virtualization, a platform to be accessible for anyone who wants to take an enjoyable nap, a safe space for user-uploaded files and a beautiful frontend for caressing the eyes!


## Backend
And now lets dive into project codes to see the actual show!
This project uses almost all the django features (not just models, views and ...)  to being a really 'django project' such as: Signals, Custom context processors, Model managers, Model Indexes, Custom permissions etc.

The project has three django apps such as:
- Accounts - for user account and other related features
- Books - for the actual content 
- Pages - for traditional pages such as home


### Models
The BookStore has ten different models that provides a neat database for the project, such as:
- CustomUser - A custom model for users using django AbstractUser model
- UserCart - For the carts of users
- UserCartBooksNumber - For the numbers of in-cart-books
- UserWish - For the wishlists of the users
- UserAddress - For addresses of the users
- Book - For books
- Category - For categories of the books
- BookImage - For additional images of the books
- Review - For reviews of the books
- ReviewReplies - For replies of reviews of the books

Also, it uses the model indexes to speed up.


### Views
The BookStore has many of views that handle the whole project interface. In addition of other views, each model has it's create, update and delete view to editing database by users outside the django admin interface but actually many of these views are to put in the admin dashboards and control panels part but since the app now has not this part, some of these views have not been used technically.

Thanks to the django auth app, many of the views are using a way to getting the correct data which is no need to put any pk or other data to working correctly, just call them and that's it!

Also, many of the views are using some tests to avoid accessing not expected users to the views and if a view needs user to login before using that, so the user will be redirected to the login page and after the successful login again to the actual view.

In this project, the django class based views have been preferred instead of function based views because of : 
- Inheritance the django generic views and mixins
- Easy-to-understand
- Avoiding the errors
- Up-to-date
- Less code


### Signal receivers
This app also has many of very useful and necessary signal receivers and this is the part that actually caries the 'super dynamic' nickname for the BookStore!

Sometimes, some processes need to be done automatically and there is no need to user to do them or programmer to repeat them everywhere in the code. So some of these receivers are helping the user and some of them are helping the programmer. For instance if a user log in with a social account(like Google), no need to set the profile image, and it will be set for the user automatically by the update_user_profile_image signal receiver. The other instance is when a user sets the number of an in-cart-book to 1, so that book will be automatically deleted from the cart by the update_user_cart_books_number_number signal receiver and no need to add some code in the views after requests and also no need to be worried about creation of a bug in this part of process!


### Templates
Django is a strong fullstack framework, so you can handle your app frontend without needing to any other frontend frameworks and APIs. So this project for literally focusing on the django itself, don't use the Django Rest Framework and for handling the frontend, it uses templates and renders them.

The base html files were extremely non-dynamic but thanks to django there is a perfect solution for this problem: the Django Template Language! So BookStore uses the DTL for making the templates dynamic. By going ahead and structuring different base files and snippets, the templates became a real framework. For example if you want to create a template for the login view, you should just extend admin-base template in the top of your template and serve your form. The rest of your template will come from the base template and your template become really a part of your site and there will be no unexpected difference. Another instance is when you want to add the book suggestions to the down of your template, you just need to add has_down_suggestions=True to your template context in the view and that's it. Even no need to add suggestion books because it uses custom context processors!


### Tests
There are over a hundred tests in this application to make sure that every part of this project are working exactly as expected. each model and view has at least one test pack (a test function or a test class) which contains many of different tests but some of them has different test packs for different actions and this makes the BookStore assured!

The typical test pack for a view that is not using a database (typically the Pages app views) checks:
- view status code
- view template using
- view correct data containing
- view incorrect data not containing
- view url right view resolving

But this tests can be known as the base tests and when it comes to test a view that uses database it becomes very different and lengthy than this list.

In short by using this tests you can make sure that the BookStore is alive and there is no easy-to-understand bugs!


## Installation
BookStore needs the python for installing so first install it. 

For installing with the Pipenv, first install the Pipenv, create a Pipenv shell (a virtual environment) then install the dependencies from the Pipfile:

```sh
pip install pipenv
pipenv shell
pipenv install 
```


## Development
Now you are ready to run the project in your local server.

First you need to add a .env file to your project level directory, so you can set the environment variables for development, because the variables defaults were set for production environment for security reasons.

Create a .env file:
```sh
cd BookStore
touch .env
```

Then generate a new django secret key:
```sh
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy codes below to .env and replace your secret key:
```sh
DJANGO_SECRET_KEY=YOUR NEW-GENERATED SECRET KEY
DJANGO_DEBUG=true
DATABASE_URL=sqlite:///db.sqlite3
DJANGO_SECURE_SSL_REDIRECT=false
DJANGO_SECURE_HSTS_PRELOAD=false
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=false
DJANGO_CSRF_COOKIE_SECURE=false
DJANGO_SESSION_COOKIE_SECURE=false
```

Migrate the migrations and finally execute the popular runserver command:
```sh
python manage.py migrate
python manage.py runserver
```
Open your browser at :
```sh
127.0.0.1:8000
```
and you will see the BookStore home page!

## Docker
BookStore is very easy to install and deploy in a Docker container.

First make sure that you have installed the Docker itself then just simply build an image using Dockerfile:

```sh
cd BookStore-app
docker build .
```
This will create the bookstore image and pull in the necessary dependencies.

Once done, To run the project with the docker compose, first replace your secret key in the docker-compose.yml file:
```sh
...
- "DJANGO_SECRET_KEY=YOUR SECRET KEY
...
```
Then lift the containers up:
```sh
docker-compose up
```
If you don't want to see the logs run the docker compose in detached mode:
```sh
docker-compose up -d
```

Or instead of taking the building and lifting the image steps separately you can easily run this command:
```sh
docker-compose up -d --build
```
And finally migrate the migrations:
```sh
docker-compose exec web python manage.py migrate
```
> Note: now you are using the postgres database not sqlite.

And that's it! Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```

### Running tests
To run the tests choose the suitable command for your situation (using docker or not):
```sh
python manage.py test
```
Or

```sh
docker-compose exec web python manage.py test
```

## License
This project is licensed under the terms of the GNU General Public license.

**Rauf Masoumi**
