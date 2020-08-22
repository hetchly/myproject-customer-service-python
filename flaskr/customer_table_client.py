import os
import boto3
import json
import logging
from collections import defaultdict
import argparse
import uuid

import datetime
from datetime import date

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

S3_BUCKET_URL = os.environ.get("S3_BUCKET_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
UPLOAD_FOLDER = "uploads"

if __package__ is None or __package__ == '':
	# uses current directory visibility
	from custom_logger import setup_logger
	from db import get_db_resource
else:
	# uses current package visibility
	from flaskr.custom_logger import setup_logger
	from flaskr.db import get_db_resource

logger = setup_logger(__name__)
table_name = 'customers'

def get_all_customers():
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.scan(
			Select='ALL_ATTRIBUTES'
	)
	customer_list = defaultdict(list)

	for item in response["Items"]:
		# if 'address' in item.keys():
		address = {}
		value = item.get('address')
		if bool(value):
			address = {
				'address_1' : item['address']['address_1'],
				'address_2' : item['address']['address_2'],
				'city' : item['address']['city'],
				'state' : item['address']['state'],
				'country' : item['address']['country'],
				'zipcode' : item['address']['zipcode'],
			}

		customer = {
			'customerId': item['customerId'],
			'firstName': item['firstName'],
			'lastName': item['lastName'],
			'email': item['email'],
			'userName': item['userName'],
			'birthDate': item['birthDate'],
			'gender': item['gender'],
			'phoneNumber': item['phoneNumber'],
			'createdDate': item['createdDate'],
			'updatedDate': item['updatedDate'],
			'profilePhotoUrl': item['profilePhotoUrl'],
			'address': address
		}
		customer_list["customers"].append(customer)
	return json.dumps(customer_list)

def get_customer(customerId):
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.get_item(
		Key={
			'customerId': customerId
		},
		ConsistentRead=True
	)
	# logger.info("Logger Response: ")
	# logger.info(response)
	if 'Item' not in response:
		raise Exception("CustomerNotFound")

	item = response['Item']

	address = {}
	value = item.get('address')
	
	if bool(value):
		address = {
			'address_1' : item['address']['address_1'],
			'address_2' : item['address']['address_2'],
			'city' : item['address']['city'],
			'state' : item['address']['state'],
			'country' : item['address']['country'],
			'zipcode' : item['address']['zipcode'],
		}

	customer = {
		'customerId': item['customerId'],
		'firstName': item['firstName'],
		'lastName': item['lastName'],
		'email': item['email'],
		'userName': item['userName'],
		'birthDate': item['birthDate'],
		'gender': item['gender'],
		'phoneNumber': item['phoneNumber'],
		'createdDate': item['createdDate'],
		'updatedDate': item['updatedDate'],
		'profilePhotoUrl': item['profilePhotoUrl'],
		'address': address
	}
	return json.dumps({'customer': customer})

def create_customer(customer_dict):
	customerId = str(customer_dict['customerId']) # str(uuid.uuid4())
	firstName = str(customer_dict['firstName'])
	lastName = str(customer_dict['lastName'])
	email = str(customer_dict['email'])
	userName = str(customer_dict['userName'])
	birthDate = str(customer_dict['birthDate'])
	gender = str(customer_dict['gender'])
	phoneNumber = str(customer_dict['phoneNumber'])
	createdDate = str(datetime.datetime.now().isoformat())
	updatedDate = "1900-01-01T00:00:00.000000"
	profilePhotoUrl = str(customer_dict['profilePhotoUrl'])

	unique = is_unique(customerId, email, userName)

	if unique:
		dynamodb = get_db_resource()
		table = dynamodb.Table(table_name)
		response = table.put_item(
			TableName=table_name,
			Item={
					'customerId': customerId,
					'firstName':  firstName,
					'lastName': lastName,
					'email': email,
					'userName': userName,
					'birthDate': birthDate,
					'gender': gender,
					'phoneNumber': phoneNumber,
					'createdDate': createdDate,
					'updatedDate': updatedDate,
					'profilePhotoUrl': profilePhotoUrl
				}
			)
		# logger.info("Logger Response: ")
		# logger.info(response)
		customer = {
			'customerId': customerId,
			'firstName': firstName,
			'lastName': lastName,
			'email': email,
			'userName': userName,
			'birthDate': birthDate,
			'gender': gender,		
			'phoneNumber': phoneNumber,
			'createdDate': createdDate,
			'updatedDate': updatedDate,
			'profilePhotoUrl': profilePhotoUrl,
		}
		return json.dumps({'customer': customer})
	else: 
		raise Exception('CustomerExists')

def update_customer(customerId, customer_dict):
	""" logger.info("Customer Dict Response: ")
	logger.info(customer_dict) """
	firstName = str(customer_dict['firstName'])
	lastName = str(customer_dict['lastName'])
	email = str(customer_dict['email'])
	userName = str(customer_dict['userName'])
	birthDate = str(customer_dict['birthDate'])
	gender = str(customer_dict['gender'])
	phoneNumber = str(customer_dict['phoneNumber'])
	updatedDate = str(datetime.datetime.now().isoformat())
	profilePhotoUrl = str(customer_dict['profilePhotoUrl'])
	address_1 = str(customer_dict['address1'])
	address_2 = str(customer_dict['address2'])
	city = str(customer_dict['city'])
	state = str(customer_dict['region'])
	country = str(customer_dict['country'])
	zipcode = str(customer_dict['zipCode'])

	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	
	try:
		response = table.update_item(
			Key={
				'customerId': customerId
			},
			UpdateExpression="""set firstName = :p_firstName,
								lastName = :p_lastName,
								email = :p_email,
								userName = :p_userName,
								birthDate = :p_birthDate,
								gender = :p_gender,
								phoneNumber = :p_phoneNumber,
								updatedDate = :p_updatedDate,
								profilePhotoUrl = :p_profilePhotoUrl, #attrName = :attrValue""",
			ExpressionAttributeNames = {
				"#attrName" : "address"
			},
			ExpressionAttributeValues = {
				':p_firstName': firstName,
				':p_lastName' : lastName,
				':p_email':  email,
				':p_userName': userName,
				':p_birthDate': birthDate,
				':p_gender':  gender,
				':p_phoneNumber': phoneNumber,
				':p_updatedDate':  updatedDate,
				':p_profilePhotoUrl':  profilePhotoUrl,
				':attrValue': {
					'address_1': address_1,
					'address_2': address_2,
					'city': city,
					'state': state,
					'country': country,
					'zipcode': zipcode
				}
			},
			ReturnValues="ALL_NEW"
		)  

	except Exception as e:
		raise Exception("CustomerNotFound")

	""" logger.info("Logger Response: ")
	logger.info(response) """

	updated_customer = response['Attributes']

	""" customer = {
		'customerId': updated['customerId'],
		'firstName': updated['firstName'],
		'lastName': updated['lastName'],
		'email': updated['email'],
		'userName': updated['userName'],
		'birthDate': updated['birthDate'],
		'gender': updated['gender'],
		'phoneNumber': updated['phoneNumber'],
		'createdDate': updated['createdDate'],
		'updatedDate': updated['updatedDate'],
		'profilePhotoUrl': updated['profilePhotoUrl'],
	} """
	
	return json.dumps({'customer': updated_customer})

def delete_customer(customerId):
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.delete_item(
		TableName=table_name,
		Key={
			'customerId': customerId
		}
	)

	logger.info("Logger Response: ")
	logger.info(response)

	if 'ConsumedCapacity' in response:
		raise Exception("CustomerNotFound")

	customer = {
		'customerId' : customerId,
	}
	return json.dumps({'customer': customer})

def is_unique(customerId, email, userName):
	"""
	Checks if email, userName, custNumber, cardNumber are unique
	Will return a list do duplicate fields
	"""
	dynamodb = get_db_resource()

	table = dynamodb.Table(table_name)

	filter_expression = Attr('customerId').eq(customerId) \
		| Attr('email').eq(email) \
		| Attr('userName').eq(userName)

	response = table.scan(
		Select='ALL_ATTRIBUTES',
		FilterExpression=filter_expression,
		ConsistentRead=True,
	)
	return len(response['Items']) == 0 

def get_max_value(attribute):
	"""Will scan the table for the maximum possible value given an attribute"""
	maximum = None
	dynamodb = get_db_resource()
	table = dynamodb.Table(table_name)
	response = table.scan(
		Select='SPECIFIC_ATTRIBUTES',
	 	AttributesToGet=[
	 		attribute
	  ],
		ConsistentRead=True,
	)

	if response['Items'] == []: 
		pass
	else: 
		maximum = max([int(m[attribute]) for m in response['Items']])
	return maximum
""" 
def customer_number_generator():
	now = datetime.datetime.now()
	max_value = get_max_value('custNumber')

	if max_value: 
		# get latest id from db and increment
		# get last 2 digits
		last_digits = str(max_value)[-2:]
		logger.info("last digits")
		logger.info(last_digits)
		new_customer_number = '099996' + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + str(int(last_digits) + 1).zfill(2)
	else: 
		new_customer_number = '099996' + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '01'
	return new_customer_number
 """
""" def card_number_generator():
	now = datetime.datetime.now()
	max_value = get_max_value('cardNumber')

	if max_value: 
		# get last 5 digits
		last_digits = str(max_value)[-5:]
		new_card_number = '623633' + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + str(int(last_digits) + 1).zfill(5)
	else: 
		new_card_number = '623633' + str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '00001'
	return new_card_number """

def get_all_images():
	s3 = boto3.resource('s3')
	my_bucket = s3.Bucket('react-customer-images')

	# Output the bucket names
	bucket_list = defaultdict(list)
	for my_bucket_object in my_bucket.objects.all():
		item = {
			"name": 'https://' + S3_BUCKET_NAME + '.' + S3_BUCKET_URL + '/' + my_bucket_object.key
		}
		bucket_list["items"].append(item)

	return json.dumps(bucket_list)

def upload_to_aws(file):
	try:
		s3_resource = boto3.resource('s3')
		bucket = s3_resource.Bucket(S3_BUCKET_NAME)
		response = bucket.Object(file.filename).put(Body=file.read());
	except ClientError as e:
		logging.error(e)
		return False
	return True