# Feamzy Dashboard - Ironhack Final Project
**by Léo Cavalcante**

<br />

### Link for the presentation
[Feamzy Dashboard - Presentation Finale pour Ironhack](https://docs.google.com/presentation/d/1moxKOG9S2QKj9dSF_KMBL5XLXZLok555vwe5zfLfFSI/edit?usp=sharing)

<br />

## Description

**Dashboard** developed to report informations from [Feamzy](https://www.feamzy.com/) app.

This dashboard was created with **Python**, using **Dash** as the web framework and **Plotly** as the visualization library.

I have learned the necessary informations via [Charming Data YouTube channel](https://www.youtube.com/channel/UCqBFsuAz41sqWcFjZkqmJqQ), a [course in Udemy](https://www.udemy.com/course/interactive-python-dashboards-with-plotly-and-dash/) and Dash and Plotly official documentations.

<br />

## Content of the folder
1. `data` folder: containing the raw databases.
2. `data_clean` folder: containing the roughly cleaned databases.
3. `static` folder: containing the images. In this case, only one: feamzy logo with blue background.
4. `cleaning_functions.py`: python code to clean the databases.
5. `feamzy_dashboard.py`: python code for the dashboard app.
6. `env`: virtual environment to run the app on local machine.
7. `stopwords.txt`: document with words to exclude from the wordclouds generated in the dashboard.
8. `requirements.txt`: document with the libraries required to be installed in the virtual environment `env` in order to run the app.
8. `Procfile`: document necessary for the deployment in **Heroku**.
9. `Jupyter Notebooks`: they were used for tests of each function in the app, but it is not formalized and they therefore don't present a pleasant reading. These files are named `Data Cleaning`, `Data Exploration` and `Data Manipulation & Visualisations.ipynb`.

<br />

## Before running the application:
1. Store the raw databases on the `data` folder.
2. Run `cleaning_functions.py`, it will send roughly cleanend databases to `data_clean` folder. These new databases will be the files that will be read by the `feamzy_dashboard` file.

<br />

## How to use it

```bash
$ # Go to the directory where the application is installed
$ cd femazy-dashboard
$
$ # Virtualenv modules installation (Mac/Unix based systems)
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Database
$ pip3 install -r requirements.txt
$
$ # Start the application (development mode)
$ python feamzy_dashboard.py
$
$ # Access the dashboard in the browser that will appear on the terminal, usually: http://127.0.0.1:5000/
```

> Note: The authentification system has to be improven for multiple users (with different logins and passwords).

<br />

## Codebase structure

The project is coded using blueprints, app factory pattern, dual configuration profile (development and production) and an intuitive structure presented bellow:

> Simplified version

```bash
< PROJECT ROOT >
   |
   |-- requirements.txt          # Development modules - SQLite storage
   |
   |-- .env                      # Inject Configuration via Environment
   |
   |-- feamzy_dashboard.py       # Start the app - WSGI gateway
   ************************************************************************
```

<br />

## Deployment instructions
I invite you to visit the following videos on YouTube describing in depth how to deploy it:
- [Charming Data - Heroku Deployment](https://www.youtube.com/watch?v=b-M2KQ6_bM4)
- [Charming Data - PythonAnywhere Deployment](https://www.youtube.com/watch?v=b-M2KQ6_bM4)

<em>PS.: I would recommend **Heroku**, which is a widely used and proven web app deployer. **PythonAnywhere** is limited to 500MB of storage and this apps exceeds it. Therefore, it is necessary to pay a subscription. </em>