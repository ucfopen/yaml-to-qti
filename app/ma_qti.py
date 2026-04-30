from lxml.etree import SubElement

from app.string_utils import sanitize_text_for_import


def convert_multiple_answer_to_qti(item, question, shuffle_answers=False):
    presentation = item.find("presentation")
    response_id = f"RESPONSE_{question['id']}"

    # Indicate if partial credit is enabled
    itemmetadata = item.find("itemmetadata")
    qtimetadata = itemmetadata.find("qtimetadata")
    qtimetadatafield = SubElement(qtimetadata, "qtimetadatafield")
    SubElement(qtimetadatafield, "fieldlabel").text = "scoring_algorithm"
    if "partial" in question and question["partial"]:
        SubElement(qtimetadatafield, "fieldentry").text = "PartialScore"
    else:
        SubElement(qtimetadatafield, "fieldentry").text = "AllOrNothing"

    # Add choices
    response_lid = SubElement(
        presentation,
        "response_lid",
        ident=response_id,
        rcardinality="Multiple",
    )
    render_choice = SubElement(response_lid, "render_choice")
    # only need to indicate that we're shuffling, default assumption is "No"
    if shuffle_answers:
        render_choice.set("shuffle", "Yes")

    correct_answers = []
    incorrect_answers = []

    for idx, a in enumerate(question["answers"], start=1):
        answer_id = f"{response_id}_CHOICE_{idx}"
        answer = a["answer"]
        response_label = SubElement(render_choice, "response_label", ident=answer_id)
        if "lock" in answer and answer["lock"]:
            response_label.set("lock", "Yes")
        if "correct" in answer and answer["correct"]:
            correct_answers.append(answer_id)
        else:
            incorrect_answers.append(answer_id)

        choice_material = SubElement(response_label, "material")
        choice_mattext = SubElement(choice_material, "mattext", texttype="text/html")
        choice_mattext.text = sanitize_text_for_import(answer["text"])

    resprocessing = SubElement(item, "resprocessing")
    outcomes = SubElement(resprocessing, "outcomes")
    SubElement(
        outcomes,
        "decvar",
        {"varname": "SCORE", "vartype": "Decimal", "minvalue": "0", "maxvalue": "100"},
    )

    respcondition = SubElement(resprocessing, "respcondition", {"continue": "No"})
    conditionvar = SubElement(respcondition, "conditionvar")
    SubElement(respcondition, "setvar", action="Set", varname="SCORE").text = "100"
    andelement = SubElement(conditionvar, "and")

    for a in correct_answers:
        SubElement(andelement, "varequal", respident=response_id).text = a
    for a in correct_answers:
        notelement = SubElement(andelement, "not")
        SubElement(notelement, "varequal", respident=response_id).text = a

    return item
