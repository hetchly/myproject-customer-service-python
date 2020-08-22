import uuid
from flask import Blueprint
from flask import Flask, json, Response, request, abort
from flask import jsonify, make_response

# Add new blueprints here
if __package__ is None or __package__ == '':
    # uses current directory visibility
    import customer_table_client
    from custom_logger import setup_logger
else:
    # uses current package visibility
    from flaskr import customer_table_client
    from flaskr.custom_logger import setup_logger

# Set up the custom logger and the Blueprint
logger = setup_logger(__name__)
customer_module = Blueprint('customers', __name__)

logger.info("Intialized customer routes")

# Allow the default route to return a health check
@customer_module.route('/')
def health_check():
    return "This a health check. Customer Management Service is up and running."

# Get all customers
@customer_module.route('/customers')
def get_all_customers():
    try:
        service_response = customer_table_client.get_all_customers()
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Get customer by customerId
@customer_module.route("/customers/<string:customerId>", methods=['GET'])
def get_customer(customerId):
    try:
        service_response = customer_table_client.get_customer(customerId)
    except Exception as e:
        logger.error(e)
        if 'CustomerNotFound' in e.args:
            abort(404)
        else:
            abort(400)
    resp = Response(service_response)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Add a new customer
@customer_module.route("/customers", methods=['POST'])
def create_customer():
    try:
        customer_dict = json.loads(request.data)
        service_response = customer_table_client.create_customer(customer_dict)
    except Exception as e:
        logger.error(e)
        if 'CustomerExists' in e.args:
            abort(405)
        else:
            abort(400)        
    resp = Response(service_response, 201)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Update customer by customerId
@customer_module.route("/customers/<customerId>", methods=['PUT'])
def update_customer(customerId):
    try:
        customer_dict = json.loads(request.data)
        service_response = customer_table_client.update_customer(customerId, customer_dict)
    except Exception as e:
        if 'CustomerNotFound' in e.args:
            abort(404)
        else:
            abort(400)
    resp = Response(service_response, 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Delete customer by customerId
@customer_module.route("/customers/<customerId>", methods=['DELETE'])
def delete_customer(customerId):
    try:
        service_response = customer_table_client.delete_customer(customerId)
    except Exception as e:
        if 'CustomerNotFound' in e.args:
            abort(404)
        else:
            abort(400)
    resp = Response(service_response, 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

@customer_module.errorhandler(400)
def bad_request(e):
    logger.error(e)
    errorResponse = json.dumps({'error': 'Bad request'})
    resp = Response(errorResponse, 400)
    resp.headers["Content-Type"] = "application/json"
    return resp

@customer_module.errorhandler(404)
def customer_not_found(e):
    logger.error(e)
    errorResponse = json.dumps({'error': 'Customer does not exist'})
    resp = Response(errorResponse, 404)
    resp.headers["Content-Type"] = "application/json"
    return resp

@customer_module.errorhandler(405)
def customer_already_exists(e):
    logger.error(e)
    errorResponse = json.dumps({'error': 'Customer already exists.'})
    resp = Response(errorResponse, 405)
    resp.headers["Content-Type"] = "application/json"
    return resp

# GET ALL UPLOADED Files
@customer_module.route('/customers/images')
def get_all_images():
    try:
        service_response = customer_table_client.get_all_images()
    except Exception as e:
        logger.error(e)
        abort(400)
    resp = Response(service_response)
    resp.headers["Content-Type"] = "application/json"
    return resp

# UPLOAD A File
@customer_module.route('/customers/upload', methods=['POST'])
def upload_to_aws():
    try:
        file_content=request.files['file']
        service_response = customer_table_client.upload_to_aws(file_content)
    except Exception as e:
        if 'CustomerNotFound' in e.args:
            abort(404)
        else:
            abort(400)
    resp = Response(service_response, 200)
    resp.headers["Content-Type"] = "application/json"
    return resp