def resolve_references(
    index: dict,
) -> list[dict]:  # responsible for resolving references
    symbols = index["symbols"]
    references = index["references"]

    function_definitions = {}  # function names and symbol here

    for symbol in symbols:
        if symbol["type"] == "function":
            name = symbol["name"]

            function_definitions.setdefault(name, []).append(symbol)

    resolved_references = []

    for reference in references:  # we check each reference collected by the indexer
        name = reference["name"]
        candidates = function_definitions.get(
            name, []
        )  # we check the current reference's name
        # exists as a function name

        if len(candidates) == 1:  # if it does, map it
            status = "resolved"
            target = candidates[0]

        elif len(candidates) > 1:  # multiple definitions found (*)
            status = "ambiguous"
            target = None

        else:  # no matching definition found for reference
            status = "unresolved"
            target = None

        # original refernce with resolution atttached
        resolved_references.append(
            {
                **reference,
                "status": status,
                "target": target,
            }
        )

    return resolved_references


def find_references(
    index: dict, symbol_name: str
) -> dict:  # allows us to search specific references
    resolved = resolve_references(index)

    definitions = [  # map all definitions of requested symbol
        symbol
        for symbol in index["symbols"]
        if symbol["name"] == symbol_name and symbol["type"] == "function"
    ]

    references = [  # map all references (calls) of requested symbol
        reference
        for reference in resolved
        if reference["name"] == symbol_name and reference["status"] == "resolved"
    ]

    return {  # display
        "name": symbol_name,
        "definitions": definitions,
        "references": references,
    }
