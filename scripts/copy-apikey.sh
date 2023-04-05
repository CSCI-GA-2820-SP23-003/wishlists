#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json wishlists:/home/vscode 
docker exec wishlists sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"