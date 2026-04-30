import copy

from lxml.etree import Element, SubElement


def convert_categorization_to_qti(item, question):
    presentation = item.find("presentation")

    # all categories will be worth the same amount of points,
    #  roughly adding up to 100
    category_score = str(100 / len(question["categories"]))

    # Add resprocessing
    # ordinarily we'd do this later, but if it exists already
    #  we can create the necessary tags within it that govern
    #  how categories are actually scored
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

    # every category will contain XML describing every possible answer
    # so let's make that tree one time so we can copy/paste it into each category
    all_answers = Element("render_choice")

    def add_answer(answer_text):
        answer_id = f"OPTION_{len(all_answers) + 1}"
        answer_el = SubElement(all_answers, "response_label", ident=answer_id)
        material = SubElement(answer_el, "material")
        SubElement(material, "mattext", texttype="text/plain").text = answer_text
        return answer_id

    # for category in question["categories"]:
    #     for answer in category["answers"]:
    #         add_answer(answer)

    for idx, c in enumerate(question["categories"], start=1):
        category = c["category"]
        category_id = f"CATEGORY_{idx}"
        response_lid = SubElement(
            presentation, "response_lid", ident=category_id, rcardinality="Multiple"
        )
        category_desc = SubElement(response_lid, "material")
        SubElement(category_desc, "mattext", texttype="text/plain").text = category[
            "description"
        ]

        respcondition = SubElement(resprocessing, "respcondition")
        conditionvar = SubElement(respcondition, "conditionvar")
        # categories can be empty
        if category["answers"] is not None and len(category["answers"]) > 0:
            for answer in category["answers"]:
                answer_id = add_answer(answer)
                SubElement(conditionvar, "varequal", respident=category_id).text = (
                    answer_id
                )
        SubElement(respcondition, "setvar", action="Add", varname="SCORE").text = (
            category_score
        )

    # master list should have all categorized answers in it
    # just have to add distractors
    if "distractors" in question:
        for distractor in question["distractors"]:
            add_answer(distractor)

    category_elements = presentation.findall("response_lid")
    for cat_element in category_elements:
        cat_element.append(copy.deepcopy(all_answers))

    return item
