# memetrics

Mongo-backed metrics mate for Metabase measures and metadata monitoring.

Pronounced muh-MEH-tricks.

## api dev setup

```bash
cd api
pip install -e .
cp .env.example .env
# edit env vars
docker run -p 27017:27017 mongo
python -m memetrics
# http://localhost:8000/docs
```
