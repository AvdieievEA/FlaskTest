from urllib3 import Request, urlopen

values = """
  {
    "description": "Test Bill",
    "payer_currency": 643,
    "shop_amount": "23.15",
    "shop_currency": 643,
    "shop_id": "112",
    "shop_order_id": 4239,
    "sign": "ad7fbe8df102bc70e28deddba8b45bb3f4e6cafdaa69ad1ecc0e8b1d4e770575"
  }
"""

headers = {
  'Content-Type': 'application/json'
}
request = Request('https://polls.apiblueprint.org/bill/create', data=values, headers=headers)

response_body = urlopen(request).read()
print(response_body)