from spur.parser import parse_php_file, extract_symbols

result = parse_php_file("tests/fixtures/example.php")

symbols = extract_symbols(result["tree"])

for symbol in symbols:
    print(symbol)
