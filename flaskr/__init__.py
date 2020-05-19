#!/usr/bin/env python
import os

from flask import Flask
from flask_cors import CORS

# Import the X-Ray modules
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# Add new blueprints here
if __package__ is None or __package__ == '':
    # uses current directory visibility
	from customer_routes import customer_module
else:
    # uses current package visibility
    from flaskr.customer_routes import customer_module

def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	CORS(app)

	# AWS X-Ray
	# Should only be available in staging and production environment, (AWS cloud)
	# will not use AWS X-ray if environment is development
	if os.environ.get("FLASK_ENV") != 'development':
		plugins = ('EC2Plugin', 'ECSPlugin')
		xray_recorder.configure(service='myproject-customer-service',plugins=plugins)
		XRayMiddleware(app, xray_recorder)
		patch_all()

	# Add a blueprint for the customers module
	app.register_blueprint(customer_module)
	
	return app