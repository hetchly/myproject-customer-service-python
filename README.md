
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

## Run and Test Locally (docker-compose)

#### Prerequisites
Make sure `FLASK_ENV` in  `flaskr/.flaskenv ` file is set to development:
```
FLASK_ENV=development
```

#### Step 1: Build and run application locally with docker compose
To test the application locally, you must first build the program. To do this, first make sure your docker daemon is running. Once running, you can build the application by issuing the ff command: 
```
$ docker-compose build
```
Once it is done building, you may now run the app using the ff command:
```
$ docker-compose up
```
```
Starting myproject-customer-service-python_dynamo-db_1 ... done
Starting myproject-customer-service-python_api_1       ... done
Attaching to myproject-customer-service-python_dynamo-db_1, myproject-customer-service-python_api_1
dynamo-db_1  | Initializing DynamoDB Local with the following configuration:
dynamo-db_1  | Port:  8000
dynamo-db_1  | InMemory:  false
dynamo-db_1  | DbPath:  .
dynamo-db_1  | SharedDb:  true
dynamo-db_1  | shouldDelayTransientStatuses:  false
dynamo-db_1  | CorsParams:  *
dynamo-db_1  |
api_1        | [INFO][customer_routes] 2020-05-09 10:22:02:MainThread:20:Intialized customer routes
api_1        | failed to get ec2 instance metadata.
api_1        |  * Serving Flask app "__init__" (lazy loading)
api_1        |  * Environment: development
api_1        |  * Debug mode: on
api_1        |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
api_1        |  * Restarting with stat
api_1        | [INFO][customer_routes] 2020-05-09 10:22:04:MainThread:20:Intialized customer routes
api_1        |  * Debugger is active!
api_1        |  * Debugger PIN: 388-367-770
```

This will create 2 containers: 
- dynamo-db (refers to the database)
- api (refers to your flask app)

#### Step 2: Set up dynamo-db local schema and test data
Now that you have the two containers running, you can check their status. I a new terminal window, and run the ff command: 
```
$ docker ps
```
```
CONTAINER ID        IMAGE                                   COMMAND                  CREATED             STATUS              PORTS                    NAMES
2331e5eb978d        myproject-customer-service-python_api   "python app.py"          22 minutes ago      Up 5 minutes        0.0.0.0:5000->5000/tcp   myproject-customer-service-python_api_1
42ed2f522ebe        amazon/dynamodb-local                   "java -jar DynamoDBL…"   3 weeks ago         Up 5 minutes        0.0.0.0:8000->8000/tcp   myproject-customer-service-python_dynamo-db_1
```
You should be seeing 2 running containers:
- myproject-customer-service-python_api_1
- myproject-customer-service-python_dynamo-db_1

You are now ready to set up the dynamo-db local table. In the same terminal window, run the ff command: 
```
 aws dynamodb create-table \
--cli-input-json file://~/environment/startup/customer-table-schema.json \
--endpoint-url http://localhost:8000
```
This will create the needed tables in the local dynamodb-db container. 

Once done, you may load data into the dynamo-db table. In the same terminal window run the ff command:
```
$ aws dynamodb batch-write-item --request-items file://~/enviroment/startup/load_customers.json --endpoint-url http://localhost:8000
```

This will load the dummy data coming from `load_customers.json` into the dynamod-db container. 

To check if the data was loaded correctly run the ff command: 
```
# Use to scan existing tables
$ aws dynamodb scan --table-name customers --endpoint-url http://localhost:8000
```

#### Step 3: Tear down
Once you are done with development, make sure to remove and stop the provisioned containers. You can do this by running the ff command:
```
$ docker-compose down
```
```
Stopping myproject-customer-service-python_api_1       ... done
Stopping myproject-customer-service-python_dynamo-db_1 ... done
Removing myproject-customer-service-python_api_1       ... done
Removing myproject-customer-service-python_dynamo-db_1 ... done
Removing network myproject-customer-service-python_default
```

In cases where you must reset the set up for dynamo-db local. You must delete the volume associated to it. To do so, run the ff commands: 

```
$ docker volume ls
local               myproject-customer-service-python_dynamodb_data
```

Remove dynamodb_data for customer-service-python
```
$ docker volume rm myproject-customer-service-python_dynamodb_data
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
