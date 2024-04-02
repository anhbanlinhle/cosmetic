//SECTION - query es

let queryElastic = async (queryData) => {
  res = await fetch('http://localhost:9200/product-v3/_search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ZWxhc3RpYzpjaGFuZ2VtZQ=='
    },
    body: JSON.stringify({
      "query": {
          "match": {
              "name": {
                  "query": queryData,
                  "minimum_should_match": "65%"
              }
          }
      }
    })
  })
  response = JSON.parse(await res.text())
  return response
}

let checkWordImportance = async (word) => {
  response = await queryElastic(word)
  let result = response.hits.hits.length

  if (result > 1)
    return 1
  if (result === 1) 
    return 0
  return -1
}

module.exports = {
  checkWordImportance
}