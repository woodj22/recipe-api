
### Introduction

An API and temporary data store used for recipe data. I have chosen to use the Flask web framework for this because it is lightweight and  relatively fast to get an API up and running.
It can also be deployed to the AWS lambda service easily and be hooked to a API gateway with almost no more overhead. This means the time to production ready is much smaller. 


### Prerequisites

- python >= 3.6
- venv installed or another environment available that can install packages from a `requirements.txt` file

### Setup

To install a local environment run: 

`python3 -m venv venv`

This will create a directory within the project repo that can be used as the development environment.

run `source venv/bin/activate` to boot into the virtual environment where we can safely install and run everything. 

To install the requirements run `pip install -r requirements.txt` from the project root.

Change the name of `config.py.example`  to `config.py`.

Update the fields in it appropriately
RECIPE_DATA_FILE_PATH= The path to the csv you wish to load in. There is one in this directory if needed. 
PAGINATION_LIMIT= The default maximum amount of items that can be displayed on one page without the user explicitly stating a different number. 

To make sure it is working run:
 `pytest`
 This will run all the tests. All should be green. See the *deployment* section to run a server to view the live API. 

 
### Usage

The work has been split into two parts the API that serves requests and a in memory database that reads and manipulates the data.

#### API

 - GET      `/recipes` - Retrieve a list of paginated recipes. Query parameters are used to filter the response. The per_page parameter is ued to determine the amount of recipes shown on one page.
 - POST     `/recipes` - Store a new recipe.
 - GET      `/recipes/{id}` - Retrieve a recipe by ID.
 - POST     `/recipes/{id}/ratings` - Upload a new recipe rating then calculate and store a new average rating. The rating uploaded must be between 1 and 5.
 - PATCH    `/recipes/{id}` - Update a recipe.
 
See the *deployment* section below to start a server to hit the endpoints.

The rating is stored in the same table as the recipes under the attribute `average_rating` and `rating_count`. The endpoint will automatically add these fields in if they are not present. 
From these two values it can calculate the new average with the new request. 

#### Database

This involves reading a csv file on load and storing the records in memory. All access is controlled via the `MemTable` class. 
The csv file that originally stores the data is loaded into it when the class is initialized. 

Warning: the data is **NOT** saved when the server is stopped.

### Testing

The test runner used is pytest. https://docs.pytest.org/en/latest/ 
This is installed as a requirement above. Run `pytest` from within venv. I have split the tests up into test types: feature and integration.

### Deployment

The waitress package is included as a requirement that can be used to deploy to production. This is a lightweight wsgi server that can be easily setup with flask.
The tutorial on deployment can be found here:

http://flask.pocoo.org/docs/1.0/tutorial/deploy/

To run the server execute:

`waitress-serve --call 'app:create_app'`

#### Troubleshooting

- No data is present/file not found error :

    Make sure you have the `RECIPE_DATA_FILE_PATH` field in the `config.py` file set to a csv file. 
If you do not have access to one, one can be found in the `data_logs` folder of this repo. 


- 500 on root page(/) :
    This is expected behaviour. Navigate to `/recipes` for live results. 

### What Next

- Better API feature tests that test values being saved to memory not just i/o.
- Use a more reliable data store.
- Error handling - Users can have a better experience and fault find themselves. ie 404 errors when a recipe does not exist.
- API validation - Good protection against malformed data. Particularly useful when the API is powered by an unstructured data store. 
- Persistant data store? see bullet 2

### Catering for different API consumers

I have added a `per_page` query field into the recipes index endpoint ( `/recipes`). 
This is so web and mobile can request different amounts of content depending on the screen size of the client. 
I have seen in some places a `requested_from` query where certain data is selected depending on the client. 
I think this should be up to the front end to decide what information they need and request the endpoints to be split up if the data is seen as to big. 

