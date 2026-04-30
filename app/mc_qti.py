from lxml.etree import SubElement

from app.string_utils import sanitize_text_for_import


def convert_multiple_choice_to_qti(item, question, shuffle_answers=False):
    presentation = item.find("presentation")
    response_id = f"RESPONSE_{question['id']}"

    # Add choices
    response_lid = SubElement(
        presentation,
        "response_lid",
        ident=response_id,
        rcardinality="Single",
    )
    render_choice = SubElement(response_lid, "render_choice")
    # only need to indicate that we're shuffling, default assumption is "No"
    if shuffle_answers:
        render_choice.set("shuffle", "Yes")
    correct_answer = None
    highest_points = 0

    # track whether we have a single respcondition tag at the end or one per answer
    # might be a more clever way of determining this - a property on the question itself, maybe?
    points_per = False

    for idx, answer in enumerate(question["answers"], start=1):
        response_label = SubElement(
            render_choice, "response_label", ident=f"CHOICE_{idx}"
        )
        if "lock" in answer["answer"] and answer["answer"]["lock"]:
            response_label.set("lock", "Yes")
        if "correct" in answer["answer"] and answer["answer"]["correct"]:
            correct_answer = idx
        if "points" in answer["answer"]:
            points_per = True
            if answer["answer"]["points"] > highest_points:
                correct_answer = idx
                highest_points = answer["answer"]["points"]

        choice_material = SubElement(response_label, "material")
        choice_mattext = SubElement(choice_material, "mattext", texttype="text/html")
        choice_mattext.text = sanitize_text_for_import(answer["answer"]["text"])
        # choice_mattext.text = answer["answer"]["text"]

    # Add correct answer processing
    # TODO: these may work as default values, but we should probably allow some variability here
    resprocessing = SubElement(item, "resprocessing")
    outcomes = SubElement(resprocessing, "outcomes")
    SubElement(
        outcomes,
        "decvar",
        {"varname": "SCORE", "vartype": "Decimal", "minvalue": "0", "maxvalue": "100"},
    )

    if points_per:
        for idx, answer in enumerate(question["answers"], start=1):
            answer_props = {"continue": "No"}
            if idx == correct_answer:
                answer_props["correctanswer"] = "Yes"
            respcondition = SubElement(resprocessing, "respcondition", **answer_props)
            conditionvar = SubElement(respcondition, "conditionvar")
            SubElement(respcondition, "setvar", action="Set", varname="SCORE").text = (
                str(answer["answer"]["points"])
            )
            SubElement(conditionvar, "varequal", respident=response_id).text = (
                f"CHOICE_{idx}"
            )
    else:
        respcondition = SubElement(resprocessing, "respcondition", {"continue": "No"})
        conditionvar = SubElement(respcondition, "conditionvar")
        SubElement(respcondition, "setvar", action="Set", varname="SCORE").text = "1"
        SubElement(conditionvar, "varequal", respident=response_id).text = (
            f"CHOICE_{correct_answer}"
        )

    return item
