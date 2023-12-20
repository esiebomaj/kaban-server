aws dynamodb create-table \
    --table-name Tasks \
    --attribute-definitions AttributeName=id,AttributeType=S AttributeName=created_at,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH AttributeName=created_at,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000
