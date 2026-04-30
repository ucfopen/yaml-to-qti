from lxml.etree import SubElement


def value_if_set(obj, prop):
    if prop in obj and obj[prop]:
        return "Yes"
    return "No"


def convert_essay_to_qti(item, question):
    presentation = item.find("presentation")

    essay_props = {
        "rce": value_if_set(question, "rce"),
        "word_count": value_if_set(question, "word_count"),
        "spell_check": value_if_set(question, "spell_check"),
        "word_limit_enabled": "No",  # default, may be overridden below
    }

    if "word_limit" in question:
        essay_props["word_limit_enabled"] = "Yes"
        if "min" in question["word_limit"]:
            essay_props["word_limit_min"] = str(question["word_limit"]["min"])
        else:
            raise Exception(f"Word limit minimum missing in question {question["id"]}")
        if "max" in question["word_limit"]:
            essay_props["word_limit_max"] = str(question["word_limit"]["max"])
        else:
            raise Exception(f"Word limit maximum missing in question {question["id"]}")

    response_str = SubElement(
        presentation,
        "response_str",
        ident=f"RESPONSE_{question["id"]}",
        rcardinality="Single",
        **essay_props,
    )

    render_fib = SubElement(response_str, "render_fib")
    SubElement(
        render_fib, "response_label", ident=f"ANSWER_{question["id"]}", rshuffle="No"
    )

    # Add resprocessing
    resprocessing = SubElement(item, "resprocessing")
    outcomes = SubElement(resprocessing, "outcomes")
    SubElement(
        outcomes,
        "decvar",
        {
            "maxvalue": "100",
            "minvalue": "0",
            "varname": "SCORE",
            "vartype": "Decimal",
        },
    )

    respcondition = SubElement(resprocessing, "respcondition", **{"continue": "No"})
    conditionvar = SubElement(respcondition, "conditionvar")
    # this is present in exported XML, but is it necessary?
    SubElement(conditionvar, "other")

    return item
