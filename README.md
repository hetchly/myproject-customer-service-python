# myproject-customer-service-python
<br/>

## Functional Requirements
- Create, Read, Update, Delete, and List Customers

## API Endpoints
```
| HTTP METHOD | URI                                      | ACTION                       |
|-------------|------------------------------------------|------------------------------|
| GET         | http://[hostname]/customers              | Gets all customers           |
| GET         | http://[hostname]/customers/<customerId> | Gets one customer            |
| POST        | http://[hostname]/customers              | Creates a new customer       |
| PUT         | http://[hostname]/customers/<customerId> | Updates an existing customer |
| DELETE      | http://[hostname]/customers/<customerId> | Deletes a customer           |
```

## Prerequisites
- Docker, Python, Flask, Git, Virtualenv https://github.com/jrdalino/development-environment-setup
- Setup CI/CD using https://github.com/jrdalino/myproject-aws-codepipeline-customer-service-terraform. This will create CodeCommit Repo, ECR Repo, CodeBuild Project, Lambda Function and CodePipeline Pipeline 
- Create ELB Service Role if it doesnt exist yet
```
$ aws iam get-role --role-name "AWSServiceRoleForElasticLoadBalancing" || aws iam create-service-linked-role --aws-service-name "elasticloadbalancing.amazonaws.com"
```

## Structure and Environment
- Clone CodeCommit Repository and navigate to working directory
```bash
$ cd ~/environment
$ git clone https://git-codecommit.ap-southeast-2.amazonaws.com/v1/repos/myproject-customer-service && cd ~/environment/myproject-customer-service
```

- Follow folder structure as per https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/
```
$ ~/environment/myproject-customer-service
├── flaskr/
│   ├── __init__.py
│   ├── app.py
│   ├── custom_logger.py
│   ├── customer_routes.py
│   ├── customer_table_client.py
│   ├── db.py
│   └── requirements.txt
├── kubernetes/
│   ├── deployment.yml
│   └── service.yml
├── tests/
│   ├── __init__.py
│   ├── customers.json
│   ├── test_curl.sh
│   ├── test_customer_routes.py
│   ├── test_db.py
│   └── test_factory.py
├── venv/
├── .gitignore
├── buildspec.yml
├── Dockerfile
└── README.md
```

- Activate virtual environment before installing flask, flask-cors and boto3
```bash
$ cd ~/environment/myproject-customer-service/myproject-customer-service
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ venv/bin/pip install flask flask-cors boto3 aws-xray-sdk
(venv) $ deactivate # To deactivate
```

## Logging
- Add custom logger ~/environment/myproject-customer-service/flaskr/custom_logger.py

## Local Development
- Setup Local DynamoDB
```
$ docker pull amazon/dynamodb-local
$ docker run -p 8000:8000 amazon/dynamodb-local
```
- Create Local DynamoDB Table
```
$ aws dynamodb create-table \
--cli-input-json file://~/environment/customers-table-schema.json \
--endpoint-url http://localhost:8000 
```
```
{
  "TableName": "customers",
  "ProvisionedThroughput": {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
  },
  "AttributeDefinitions": [
    {
      "AttributeName": "customerId",
      "AttributeType": "S"
    }
  ],
  "KeySchema": [
    {
      "AttributeName": "customerId",
      "KeyType": "HASH"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "name_index",
      "KeySchema": [
        {
          "AttributeName": "customerId",
          "KeyType": "HASH"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      },
      "ProvisionedThroughput": {
        "ReadCapacityUnits": 5,
        "WriteCapacityUnits": 5
      }
    }
  ]
}
```

## Development
- You may also copy everything from Github repo to CodeCommit repo
```
$ rsync -rv --exclude=.git ~/environment/myproject-customer-service-python/ ~/environment/myproject-customer-service/
```
OR
- Add application factory               ~/environment/myproject-customer-service/flaskr/__init__.py
- Create the dynamodb table using       https://github.com/jrdalino/myproject-aws-dynamodb-customer-service-terraform
- Add static database                   ~/environment/myproject-customer-service/tests/customers.json
- Connect to the database               ~/environment/myproject-customer-service/flaskr/db.py

- Add customer dynamodb table client    ~/environment/myproject-customer-service/flaskr/customer_table_client.py
- Add customer routes                   ~/environment/myproject-customer-service/flaskr/customer_routes.py
- Add app                               ~/environment/myproject-customer-service/flaskr/app.py


## Run
- Run locally
```bash
$ cd flaskr
$ python app.py
$ curl http://localhost:5000
```

## Testing
- Add tests using curl ~/environment/myproject-customer-service/tests/test_curl.sh
- Replace hostname and port variables
- Run tests using curl
```
$ cd ~/environment/myproject-customer-service/tests
$ chmod a+x test_curl.sh
$ ./test_curl.sh
```
- Install pytest and coverage to test and measure your code, pytest-flask and moto to mock your flask server and mock dynamodb 
```
(venv) $ venv/bin/pip install pytest coverage pytest-flask moto
```
- Add static database ~/environment/myproject-customer-service/tests/customers.json
- Add tests for factory ~/environment/myproject-customer-service/tests/test_factory.py
- Add tests for database ~/environment/myproject-customer-service/tests/test_db.py
- Add ~/environment/myproject-customer-service/tests/__init__.py
- Add tests for customer routes ~/environment/myproject-customer-service/tests/test_customer_routes.py
- Run tests and measure code coverage
```
$ pytest
$ coverage run -m pytest
$ coverage report
$ coverage html # open htmlcov/index.html in a browser
```
- TODO: Add tests for other AWS Services https://github.com/spulec/moto

## Containerize
- Generate ~/environment/myproject-customer-service/flaskr/requirements.txt
```bash
$ pip freeze > requirements.txt
```
- Add Docker File ~/environment/myproject-customer-service/Dockerfile
- Build, Tag and Run the Docker Image locally. (Replace AccountId and Region)
```bash
$ cd ~/environment/myproject-customer-service
$ docker build -t myproject-customer-service .
$ docker tag myproject-customer-service:latest 707538076348.dkr.ecr.ap-southeast-1.amazonaws.com/myproject-customer-service:latest
$ docker run -e AWS_ACCESS_KEY_ID=<REPLACE_ME> -e AWS_SECRET_ACCESS_KEY=<REPLACE_ME> -d -p 5000:5000 myproject-customer-service:latest
$ curl http://localhost:5000
```
- Note: For manual deployment only, create the image repositories manually
```bash
$ aws ecr create-repository --repository-name myproject-customer-service
```
- Push Docker Image to ECR and validate
```bash
$ $(aws ecr get-login --no-include-email)
$ docker push 707538076348.dkr.ecr.ap-southeast-1.amazonaws.com/myproject-customer-service:latest
$ aws ecr describe-images --repository-name myproject-customer-service
```

## Run and Test Locally
```
$ docker-compose up
```
```
version: '3'
services:
  # https://github.com/aws-samples/aws-sam-java-rest/issues/1
  dynamo-db:
    image: amazon/dynamodb-local
    ports:
      - '8000:8000'
    volumes:
      - dynamodb_data:/home/dynamodblocal
    working_dir: /home/dynamodblocal
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ."

  api:
    build: .
    volumes:
      - ./flaskr:/flaskr
    ports:
      - '5000:5000'
    links: 
      - dynamo-db
volumes:
  dynamodb_data:
```

## Change Database to DynamoDB on AWS

## Pre-Deployment
- Add .gitignore file ~/environment/myproject-customer-service/.gitignore
- Add Kubernetes Deployment and Service Yaml files ~/environment/myproject-customer-service/kubernetes/deployment.yml and ~/environment/myproject-customer-service/kubernetes/service.yml

## Manual Deployment
- Create k8s Deployment and Service
```
$ cd ~/environment/myproject-customer-service/kubernetes
$ kubectl apply -f deployment.yml
$ kubectl apply -f service.yml
$ kubectl get all
```

## Automated Deployment
- Review https://github.com/jrdalino/myproject-aws-codepipeline-customer-service-terraform
- Add Buildspec Yaml file ~/environment/myproject-customer-service/buildspec.yml
- Make changes, commit and push changes to CodeCommit repository to trigger codepipeline deployment to EKS
```bash
$ git add .
$ git commit -m "Initial Commit"
$ git push origin master
```
- Create k8s Service (You only have to do this once)
```
$ cd ~/environment/myproject-customer-service/kubernetes
$ kubectl apply -f service.yml
$ kubectl get all
```

## (Optional) Clean up
```bash
$ kubectl delete -f service.yml
$ kubectl delete -f deployment.yml
$ aws ecr delete-repository --repository-name myproject-customer-service --force
$ aws codecommit delete-repository --repository-name myproject-customer-service
$ rm -rf ~/environment/myproject-customer-service
$ docker ps
$ docker kill <CONTAINER_ID>
$ docker images
$ docker system prune -a
```
