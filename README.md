# WutongSearch
a search engine crwaler based on python selenium



### install

pip install wsearch

### Usage

```python
from wsearch import WutongSearch
engine = WutongSearch("config.yaml")
result = engine.search(keyword="apple", search_engine='bing', num_pages_per_keyword=2)
print(result) ### a list of (url,title)

```

