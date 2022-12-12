# ![Bildschirmfoto 2022-10-01 um 12 34 02](https://user-images.githubusercontent.com/76044729/193405379-31b70901-9888-4733-a4bd-24691b49c3fc.png)
A opensource smarthome-platform that monitors sensor-data coming from your devices!

# Quick-Set-Up

Clone the repository:

````
git clone https://github.com/Drizzr/WebProject/
````

Install the required libaries:

````
pip3 install -m requirements.txt
````

To run the project you either have to connect to your redis server by changing the conifig.py file or connect to your localhost redis-db (default):
````
redis-server 
````

You also might want to connect to your email-server if you want to test you can run a simulated python-email-server on your local machine with the following command:
````
python3 -m smtpd -n -c DebuggingServer localhost:8025
````

Now you can start the backend by the following command (make sure to run this command in the WebProject directory):
````
python3 main.py
````

Then you have to create all the role entries in your database. Run the following command to do so (make sure to run the server in background while doing this):
````
python3 db_querys.py
````
(before you first sign up to your account make sure to write your email into the config.py file in order to have access to admin tools)

To register a worker that communicates with the redis-db and handels time-expendive task (ip-geolocation, sending emails)
run the following commands (make sure to run this command in the WebProject directory):
````
rq worker urbanwaters-tasks  
````

# Website Overview
__Once you logged in you an overview of all registered sensors and rooms:__

![Bildschirm­foto 2022-12-10 um 12 34 38](https://user-images.githubusercontent.com/76044729/206853094-8c225f1a-7ae0-4bd4-8e1a-879ba7e002d1.png)


__You can also track your sensor data with dynamic charts:__

![Bildschirm­foto 2022-12-10 um 12 31 05](https://user-images.githubusercontent.com/76044729/206853085-9b051db2-b5f9-4a0a-b6ef-79fa3e43ed72.png)


__The Website also comes with an custom admin-panel built on top of Flask-Admin:__

![Home - Admin](https://user-images.githubusercontent.com/76044729/206853178-5bfca8ec-a586-4796-8b93-f503c57d9642.jpg)


