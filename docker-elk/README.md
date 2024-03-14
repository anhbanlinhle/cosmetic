Firstly, run the following command to initialize accounts and roles for Elasticsearch

```
docker-compose up setup
```

To build containers

```
docker-compose up -d
```

> **_IMPORTANT_**

For the first installation, use this Curl to change the license from <i>Trial</i> to <i>Basic</i>

```
curl -X POST "localhost:9200/_license/start_basic?acknowledge=true&pretty"
```
