from lxml.etree import SubElement


def convert_true_false_to_qti(item, question):
    presentation = item.find("presentation")
    response_id = f"RESPONSE_{question['id']}"

    response_lid = SubElement(
        presentation, "response_lid", ident=response_id, rcardinality="Single"
    )

    render_choice = SubElement(response_lid, "render_choice")
    response_label_true = SubElement(
        render_choice, "response_label", ident="true_choice"
    )
    material_true = SubElement(response_label_true, "material")
    SubElement(material_true, "mattext", texttype="text/html").text = "True"
    response_label_false = SubElement(
        render_choice, "response_label", ident="false_choice"
    )
    material_false = SubElement(response_label_false, "material")
    SubElement(material_false, "mattext", texttype="text/html").text = "False"

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
    correct_answer = "true_choice" if question["answer"] else "false_choice"
    SubElement(conditionvar, "varequal", respident=response_id).text = correct_answer

    SubElement(respcondition, "setvar", varname="SCORE", action="Set").text = "100"

    return item
