""" import boto3
import os

def get_db_resource():
	# check environment as long as its not development
	dynamodb = boto3.resource('dynamodb', 
				region_name='ap-southeast-1',
				# endpoint_url='http://dynamo-db:8000/',
        		# aws_access_key_id='x',
      			# aws_secret_access_key='x'
		)
	return dynamodb
	if os.environ.get("FLASK_ENV") != 'development':
		dynamodb = boto3.resource('dynamodb',
			region_name='ap-southeast-1')
	else:
		dynamodb = boto3.resource('dynamodb', 
			region_name='ap-southeast-1',
			endpoint_url='http://dynamo-db:8000/',
  		aws_access_key_id='x',
			aws_secret_access_key='x'
		)

	return dynamodb """
import boto3
import os
def get_db_resource():
	# check environment as long as its not development
	if os.environ.get("FLASK_ENV") != 'development':
		dynamodb = boto3.resource('dynamodb',
			region_name='ap-southeast-1')
	else:
		dynamodb = boto3.resource('dynamodb',
			region_name='ap-southeast-1',
			endpoint_url='http://dynamo-db:8000/',
  		aws_access_key_id='x',
			aws_secret_access_key='x'
		)
	return dynamodb