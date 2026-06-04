make rebuild --- Level1 

startup order

1. ClickHouse
2. OpenSearch
3. DynamoDB Local
4. Embedding Service
5. OpenSearch Init
6. Seed Job
7. Indexer Service
8. RAG Service
9. API Gateway


yohannesm@Yohanness-MacBook-Pro-2 ai-analytics-copilot % aws dynamodb list-tables \
  --endpoint-url http://localhost:8005 \
  --region eu-west-2
{
    "TableNames": []
}

yohannesm@Yohanness-MacBook-Pro-2 ai-analytics-copilot % docker-compose ps
             Name                            Command                  State                                     Ports                               
----------------------------------------------------------------------------------------------------------------------------------------------------
ai-analytics-copilot_seed-job_1   python ingest_clickhouse.py      Exit 0                                                                           
api-gateway                       uvicorn main:app --host 0. ...   Up             0.0.0.0:8000->8000/tcp                                            
clickhouse                        /entrypoint.sh                   Up (healthy)   0.0.0.0:8123->8123/tcp, 0.0.0.0:9000->9000/tcp, 9009/tcp          
dynamodb-local                    java -jar DynamoDBLocal.ja ...   Up             0.0.0.0:8005->8000/tcp                                            
embedding-service                 uvicorn main:app --host 0. ...   Up             0.0.0.0:8002->8002/tcp                                            
indexer-service                   python main.py                   Exit 1                                                                           
opensearch                        ./opensearch-docker-entryp ...   Up (healthy)   0.0.0.0:9200->9200/tcp, 9300/tcp, 0.0.0.0:9600->9600/tcp, 9650/tcp
opensearch-init                   python init_index.py             Exit 0                                                                           
rag-service                       uvicorn main:app --host 0. ...   Up             0.0.0.0:8001->8001/tcp                                            

yohannesm@Yohanness-MacBook-Pro-2 ai-analytics-copilot % curl http://localhost:8002/health
{"status":"ok"}%                                 








bash-3.2$ curl -k -u admin:Opensearch2026\!Aa https://localhost:9200/_cluster/health?pretty
{
  "cluster_name" : "docker-cluster",
  "status" : "yellow",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "discovered_master" : true,
  "discovered_cluster_manager" : true,
  "active_primary_shards" : 7,
  "active_shards" : 7,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 2,
  "delayed_unassigned_shards" : 0,
  "number_of_pending_tasks" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 77.77777777777779
}


bash-3.2$ curl -k -u admin:Opensearch2026\!Aa https://localhost:9200/_cat/indices?v
health status index                        uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   github-repos                 ZmpQ_E6NSa6xTSCY9WP7Dg   1   1         12            0      107kb          107kb
green  open   top_queries-2026.06.04-14688 v4Ojfrc4QKOk_HGZtoBUFA   1   0          6            0       91kb           91kb
green  open   .plugins-ml-config           RRKW_MYmTT-mUHgFgkCuew   1   0          1            0        4kb            4kb
green  open   .opensearch-observability    3dxlc2ibQI-hKhsdbuw25w   1   0          0            0       208b           208b
green  open   .opendistro_security         YpP5hywLQu-nTtWmcVKNRg   1   0         10            0       83kb           83kb
yellow open   security-auditlog-2026.06.04 rvFUSFXFTCW-FLdeoVtLwA   1   1         28            0    185.8kb        185.8kb




curl -k -u admin:Opensearch2026\!Aa \
"https://localhost:9200/github-repos/_search" \
-H "Content-Type: application/json" \
-d '{
  "size": 3,
  "query": {
    "match": {
      "description": "machine learning"
    }
  }
}'

