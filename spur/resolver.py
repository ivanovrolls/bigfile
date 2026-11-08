def resolve_references(index: dict) -> list[dict]:
    symbols = index["symbols"]
    references = index["references"]

    function_definitions = {}

    for symbol in symbols:
        if symbol["type"] == "function":
            name = symbol["name"]

            function_definitions.setdefault(name, []).append(symbol)

    resolved_references = []

    for reference in references:
        name = reference["name"]
        candidates = function_definitions.get(name, [])

        if len(candidates) == 1:
            status = "resolved"
            target = candidates[0]

        elif len(candidates) > 1:
            status = "ambiguous"
            target = None

        else:
            status = "unresolved"
            target = None

        resolved_references.append(
            {
                **reference,
                "status": status,
                "target": target,
            }
        )

    return resolved_references
