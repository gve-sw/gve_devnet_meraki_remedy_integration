# GVE DevNet Meraki Remedy Integration
This repository contains code to integrate Meraki alerts with BMC Remedy incident tickets. When a Meraki alert for a router, switch, or access point going down is generated, a ticket is automatically created with BMC Remedy. This code also attempts to remove the possibility of duplicate tickets. For example, if a switch goes down, then all the access points connected to that switch go down as well. It is unhelpful to create tickets for the switch and all the access points, so this code attempts to only create a ticket for the switch and not the access points as well. There are limitations to this feature though because it is based on the assumption that access points are connected to switches and switches are connected to routers. If the environment does not have this topology, there may be issues when creating tickets. Note, this code also depends on when the order the alerts are generated. For instance, if the alert for a switch going down is generated before the alert for the access point going down, then the code works as it should. If the alert for the access point is generated first, however, then both tickets will be created. In my experience, the alerts for the switch are generated before the access point if the switch goes down, but I have experienced issues with the router going down but the alert for the switch connected to the router going down is generated first.

![/IMAGES/workflow.png](/IMAGES/workflow.png)

## Contacts
* Danielle Stacy

## Solution Components
* Python 3.10
* Flask
* SQLite
* Meraki Alerts
* Meraki APIs
* BMC Remedy
* ngrok

## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`
3. Click on `Enable access to the Cisco Meraki Dashboard API`
4. Go to `My Profile > API access`
5. Under API access, click on `Generate API key`
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

#### ngrok
The webhook receivers for Meraki Alerts require https URLs. Since this code runs on http://localhost:5000, it requires a forwarding address with https in order to receive the webhooks. To emulate this, ngrok is used.
Follow these instructions to set up ngrok:
1. Create a free account or login to [Ngrok](https://ngrok.com/).
2. Retrieve your auth token by navigating to `Getting Started` > `Your Authtoken` on the menu on the left-hand side. Copy the token on this page.
3. Then install the client library depending on your OS [here](https://ngrok.com/download).
4. Once you have ngrok installed, update the ngrok configuration file with your auth token by running the following command on the terminal/command prompt: 
```
ngrok authtoken [yourtoken]
```
replacing [yourtoken] with the authtoken you copied in Step 2.

5. Start the ngrok tunnel for port 5000 with the command:
```
ngrok http 5000
```

#### Meraki Alerts
In order to generate webhooks for the Meraki Alerts this code is written to create Remedy tickets for, follow these steps:
1. Login to the Meraki dashboard.
2. In the left-hand menu, navigate to `Network-wide` >  `Configure` > `Alerts`.
3. Here, select the appropriate checkboxes for which events should generate alerts. Under Wireless, select `A gateway goes offline for 5 minutes` and `A repeater goes offline for 5 minutes`. This will generate alerts for when access points are offline for 5 minutes. Under Security appliance, select `A security appliance goes offline for 5 minutes`. This will generate alerts for when routers are offline for 5 minutes. Under Switch, select `A switch goes offline for 5 minutes`. This will generate alerts for when switches are offline for 5 minutes. To guarantee that the alerts are sent in the right order, you can modify the amount of time that should pass before an alert is generated. For instance, keep the security appliance at 5 minutes, but increase the time of the switch to 10 minutes and the access point to 15 minutes. Thus, if a router goes down, then after 5 minutes, a ticket will be created for it once the alert is generated but it will take 5 more minutes before the switch connected to the router will generate an alert.
4. Next, you need to add the webhook receiver to send the alert webhooks to. Under the `Webhooks` section, add an HTTP receiver. Give it a name and copy the https forwarding URL from ngrok as the receiver URL.
5. Then, add the webhook receiver as a default recipient of alerts. Scroll to the top of the page to the `Alerts Settings` section, add the webhook receiver that you just created to the Default recipients list.
6. Scroll to the bottom of the page and click `Save` to save these changes.

> For more information about Meraki Alerts and Notifications, please click [here](https://documentation.meraki.com/General_Administration/Cross-Platform_Content/Alerts_and_Notifications).

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_meraki_remedy_integration.git`
2. Add the BMC Remedy credentials, Meraki API key, Meraki organization name, and Meraki network name to the environmental variables in the .env file:
```python
REMEDY_URL = "Remedy domain goes here"
REMEDY_USERNAME = "Remedy username goes here"
REMEDY_PASSWORD = "Remedy password goes here"

MERAKI_TOKEN = "Meraki API key goes here"
MERAKI_ORG = "Meraki organization name goes here"
MERAKI_NETWORK = "Meraki network name goes here"
```
> For more information about environmental variables, read [this article](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)
3. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
4. Install the requirements with `pip3 install -r requirements.txt`


## Usage
The first step to using this code is to create the database that will hold the connection and status information of the routers, switches, and access points in the network. To do this, run the command:
```
$ python3 db.py
```
Once this code completes, it will print out three empty lists representing the items in the routers, switches, and aps tables. It will also create the database file sqlite.db.

![/IMAGES/create_db.png](/IMAGES/create_db.png)

The next step is to populate the database with the devices in your Meraki network. To do this, run the command:
```
$ python3 populate.py
```
Once the code completes, it will print out the contents of the routers, switches, and aps tables in the database.
Note: this code is written with the assumption that the switches are connected to routers and the access points are connected to switches. If this is not the case in your environment, it will likely generate an error. To remedy this, add more conditions in the file. For example, there is a condition to check if the device types connected to one another are an 'AP' and 'switch'. Suppose you have switches connected to switches in your environment, you will need to add a condition to the code that checks if the device types are both 'switch' and then write the code to handle this condition.

![/IMAGES/populate_db.png](/IMAGES/populate_db.png)

Now to start the web server that will receive the Meraki webhook alerts and create Remedy tickets, run the command:
```
$ flask run
```
As this code runs, it will print out the alerts it receives from Meraki. It will also print out whether a Remedy ticket was created or not.

![/IMAGES/alert.png](/IMAGES/alert.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
