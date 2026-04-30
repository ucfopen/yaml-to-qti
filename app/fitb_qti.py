import copy

from lxml.etree import Element, SubElement

TYPE_DICT = {"open": "openEntry", "dropdown": "dropdown", "bank": "wordbank"}
SUBTYPE_DICT = {
    "contains": "TextContainsAnswer",
    "close": "TextCloseEnough",
    "match": "TextEquivalence",
    "multiple": "TextInChoices",
    "regex": "TextRegex",
}


def convert_fill_in_the_blank_to_qti(item, question):
    presentation = item.find("presentation")
    question_id = f"QUESTION_{question["id"]}"

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

    # for questions that use word banks for any of the blanks, it looks like
    #  every blank will have to keep track of every word and distractor
    # keep track of them all and then append everywhere necessary at the end
    wordbank_options = Element("render_choice")
    wordbank_elements = []

    # each blank will be worth the same number of points out of 100
    blank_points = 100 / len(question["blanks"])

    # for idx, blank in enumerate(question["blanks"]):
    for blank_parent in question["blanks"]:
        blank = blank_parent["blank"]
        response_id = f"response_{blank["id"]}"
        response_lid = SubElement(presentation, "response_lid", ident=response_id)

        is_wordbank_blank = False

        scoring_algorithm = None
        if "subtype" in blank:
            scoring_algorithm = SUBTYPE_DICT[blank["subtype"]]
        elif blank["type"] == "dropdown":
            scoring_algorithm = "Equivalence"
        elif blank["type"] == "bank":
            is_wordbank_blank = True
            wordbank_elements.append(response_lid)
            scoring_algorithm = "TextEquivalence"
        else:
            raise Exception(
                f"Scoring algorithm indeterminable in question {question["title"]}"
            )

        render_choice = (
            None if is_wordbank_blank else SubElement(response_lid, "render_choice")
        )

        # used when rendering the outcomes area
        # this should be the same for most things most of the time,
        #  but may change
        correct_choice = f"{blank["id"]}-0"

        # how this blank's answer or answers are rendered in XML depends
        #  on the type and subtype, some being more complicated than others
        if "answers" in blank:
            main_material = SubElement(response_lid, "material")
            SubElement(main_material, "mattext", texttype="text/plain").text = blank[
                "answers"
            ][0]
            for answer_index, answer in enumerate(blank["answers"]):
                answer_id = f"{blank["id"]}-{answer_index}"
                response_label = SubElement(
                    render_choice,
                    "response_label",
                    ident=answer_id,
                    answer_type=TYPE_DICT[blank["type"]],
                    scoring_algorithm=scoring_algorithm,
                )
                if blank["type"] == "dropdown":
                    response_label.set("position", str(answer_index + 1))
                    if answer_index == 0:
                        correct_choice = answer_id
                if is_wordbank_blank:
                    correct_choice = answer_id
                material = SubElement(response_label, "material")
                SubElement(material, "mattext", texttype="text/plain").text = answer

        # assume only one answer
        else:
            response_label = SubElement(
                wordbank_options if is_wordbank_blank else render_choice,
                "response_label",
                ident=f"{blank["id"]}-0",
                answer_type=TYPE_DICT[blank["type"]],
                scoring_algorithm=scoring_algorithm,
            )
            first_material = SubElement(response_lid, "material")
            SubElement(first_material, "mattext", texttype="text/plain").text = blank[
                "answer"
            ]
            second_material = SubElement(response_label, "material")
            SubElement(second_material, "mattext", texttype="text/plain").text = blank[
                "answer"
            ]

        respcondition = SubElement(resprocessing, "respcondition")
        conditionvar = SubElement(respcondition, "conditionvar")
        SubElement(conditionvar, "varequal", respident=response_id).text = (
            correct_choice
        )
        SubElement(respcondition, "setvar", action="Add", varname="SCORE").text = str(
            blank_points
        )

    if "distractors" in question:
        for distractor_index, distractor in enumerate(question["distractors"], start=1):
            response_label = SubElement(
                wordbank_options,
                "response_label",
                ident=f"{question_id}_DISTRACTOR_{distractor_index}",
                answer_type=TYPE_DICT["bank"],
                scoring_algorithm="TextEquivalence",
            )
            material = SubElement(response_label, "material")
            SubElement(material, "mattext", texttype="text/plain").text = distractor

    for wordbank in wordbank_elements:
        wordbank.append(copy.deepcopy(wordbank_options))

    return item
