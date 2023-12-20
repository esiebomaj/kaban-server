aws dynamodb create-table \
    --table-name Tasks \
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=created_at,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH AttributeName=created_at,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000


aws dynamodb update-table \
    --table-name Tasks \
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=priority,AttributeType=S \
    --global-secondary-index-updates \
        "CreateIndex={IndexName=PriorityIndex,KeySchema=[{AttributeName=id,KeyType=HASH},{AttributeName=priority,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}}" \
    --endpoint-url http://localhost:8000

aws dynamodb create-table --table-name Tasks --attribute-definitions AttributeName=id,AttributeType=S AttributeName=created_at,AttributeType=S --key-schema AttributeName=id,KeyType=HASH AttributeName=created_at,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --endpoint-url http://localhost:8000
aws dynamodb update-table --table-name Tasks --attribute-definitions AttributeName=id,AttributeType=S AttributeName=priority,AttributeType=N --global-secondary-index-updates "Create={IndexName=PriorityIndex,KeySchema=[{AttributeName=id,KeyType=HASH},{AttributeName=priority,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}}"  --endpoint-url http://localhost:8000