# vectorai
<h1>rest API for passport image processing</h1>

<h2>Installation</h2>

1) Build the application:  <strong>docker-compose build</strong><br>
2) Start the application and stop with ctrl+c: <strong>docker-compose up</strong><br>
3) Migrate data: <strong>docker-compose run --rm vectorai /bin/bash -c "cd vectorai; ./manage.py migrate"</strong><br>
4) Initialize data loading fixtures: <strong>docker-compose run --rm vectorai /bin/bash -c "cd vectorai; ./manage.py loaddata countries.json"</strong><br>

<h2>Instructions</h2>

Upload file to process: https://your-ip-or-domain:8000/restapi/upload/<br>
Process or delete image: https://your-ip-or-domain:8000/restapi/check/<uploaded_filename\>/<br><br>

Process image with no storing on server:  https://your-ip-or-domain:8000/restapi/check/
