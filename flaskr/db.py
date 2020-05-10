import boto3

def get_db_resource():
		dynamodb = boto3.resource('dynamodb', 
				region_name='ap-southeast-1',
				# endpoint_url='http://dynamo-db:8000/',
        		# aws_access_key_id='x',
      			# aws_secret_access_key='x'
		)
		return dynamodb