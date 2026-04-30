from lxml.etree import SubElement

from app.string_utils import sanitize_text_for_import


def convert_ordering_to_qti(item, question):
    presentation = item.find("presentation")
    question_id = f"QUESTION_{question['id']}"

    response_lid = SubElement(
        presentation, "response_lid", ident=question_id, rcardinality="Ordered"
    )

    resprocessing = SubElement(item, "resprocessing")
    outcomes = SubElement(resprocessing, "outcomes")
    SubElement(
        outcomes,
        "decvar",
        {
            "defaultval": str(question["points"]),
            "varname": "ORDERSCORE",
            "vartype": "Integer",
        },
    )
    respcondition = SubElement(resprocessing, "respcondition", {"continue": "No"})
    # creating this now so we can append responses to it later in the correct order
    conditionvar = SubElement(respcondition, "conditionvar")
    SubElement(respcondition, "setvar", action="Set", varname="Score").text = "100"

    render_extension = SubElement(response_lid, "render_extension")

    # check to see if labels are specified, handle top and bottom individually
    labels = "labels" in question

    if labels:
        if "top" not in question["labels"]:
            raise Exception(f"Top label missing in question {question["id"]}")
        top_label = SubElement(render_extension, "material", position="top")
        SubElement(top_label, "mattext").text = question["labels"]["top"]

    ims_render_object = SubElement(render_extension, "ims_render_object")
    if "paragraph" in question and question["paragraph"]:
        ims_render_object.set("orientation", "Row")
    flow_label = SubElement(ims_render_object, "flow_label")

    for idx, answer in enumerate(question["answers"], start=1):
        answer_id = f"QUESTION_{question_id}_RESPONSE_{idx}"
        # the visual objects for each response are in reverse order in exports
        # see if importing them in true order breaks anything?
        response_label = SubElement(flow_label, "response_label", ident=answer_id)
        material = SubElement(response_label, "material")
        SubElement(material, "mattext").text = sanitize_text_for_import(
            answer["answer"]
        )

        # the scorable element for each response
        SubElement(conditionvar, "varequal", respident=question_id).text = answer_id

    if labels:
        if "bottom" not in question["labels"]:
            raise Exception(f"Bottom label missing in question {question["id"]}")
        bottom_label = SubElement(render_extension, "material", position="bottom")
        SubElement(bottom_label, "mattext").text = question["labels"]["bottom"]

    return item
