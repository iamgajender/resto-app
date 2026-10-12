#/bin/bash


m_s_list=("home" "meals" "beverages" "orders")

db=$DB_NAME
latest_tag=18
echo "this is the our working db: $db"


for i in "${m_s_list[@]}" ;
do 
docker build -t "${DOCKER_USERNAME}/$i:${latest_tag}" "./$i" -f  "$i/Dockerfile"
done









