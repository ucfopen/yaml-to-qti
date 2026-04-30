from lxml.etree import SubElement


def convert_formula_to_qti(item, question):
    presentation = item.find("presentation")
    response_id = f"RESPONSE_{question['id']}"

    response_str = SubElement(
        presentation, "response_str", ident=response_id, rcardinality="Single"
    )
    render_fib = SubElement(response_str, "render_fib", fibtype="Decimal")
    # will there ever only be one of these?
    SubElement(render_fib, "response_label", ident="answer1")

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

    respcondition_correct = SubElement(resprocessing, "respcondition", title="correct")
    conditionvar = SubElement(respcondition_correct, "conditionvar")
    SubElement(conditionvar, "other")
    SubElement(respcondition_correct, "servar", varname="SCORE", action="Set").text = (
        "100"
    )

    respcondition_incorrect = SubElement(
        resprocessing, "respcondition", title="correct"
    )
    conditionvar = SubElement(respcondition_incorrect, "conditionvar")
    not_other = SubElement(conditionvar, "not")
    SubElement(not_other, "other")
    SubElement(
        respcondition_incorrect, "servar", varname="SCORE", action="Set"
    ).text = "0"

    itemproc = SubElement(item, "itemproc_extension")
    calculated = SubElement(itemproc, "calculated")

    settings = question["settings"]

    if "scientific" not in settings:
        raise Exception(
            f"Question {question["id"]} missing scientific notation setting"
        )
    is_scientific_notation = settings["scientific"]
    if is_scientific_notation:
        SubElement(calculated, "answer_tolerance", margin_type="").text = "0"
    else:
        SubElement(
            calculated, "answer_tolerance", margin_type=settings["margin_type"]
        ).text = str(settings["margin"])

    formulas = SubElement(
        calculated,
        "formulas",
        decimal_places=str(settings["decimals"]),
        scientific_notation=str(is_scientific_notation).lower(),
    )
    SubElement(formulas, "formula").text = question["formula"]

    vars = SubElement(calculated, "vars")
    for variable in question["variables"]:
        v_obj = variable["variable"]
        var = SubElement(vars, "var", name=v_obj["name"], scale=str(v_obj["decimals"]))
        SubElement(var, "min").text = str(v_obj["min"])
        SubElement(var, "max").text = str(v_obj["max"])

    var_sets = SubElement(calculated, "var_sets")
    for answer_index, answer in enumerate(question["answers"], start=1):
        answer_obj = answer["answer"]
        var_set = SubElement(
            var_sets, "var_set", ident=f"{response_id}_SOLUTION_{answer_index}"
        )
        for key in answer_obj:
            if key != "result":
                SubElement(var_set, "var", name=key).text = str(answer_obj[key])
            else:
                SubElement(var_set, "answer").text = str(answer_obj[key])

    return item
