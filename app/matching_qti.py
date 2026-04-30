import copy
import random

from lxml.etree import Element, SubElement


def convert_matching_to_qti(item, question, shuffle=True):
    presentation = item.find("presentation")

    # Indicate if partial credit is enabled
    itemmetadata = item.find("itemmetadata")
    qtimetadata = itemmetadata.find("qtimetadata")
    qtimetadatafield = SubElement(qtimetadata, "qtimetadatafield")
    SubElement(qtimetadatafield, "fieldlabel").text = "scoring_algorithm"
    if "partial" in question and question["partial"]:
        SubElement(qtimetadatafield, "fieldentry").text = "PartialDeep"
    else:
        SubElement(qtimetadatafield, "fieldentry").text = "DeepEquals"

    # all pairs will be worth the same amount of points,
    #  roughly adding up to 100
    pair_score = str(100 / len(question["pairs"]))

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

    # every left side element will contain XML describing every possible
    #  right side element, so let's make that tree one time so we can
    #  copy/paste it everywhere later
    all_answers = Element("render_choice")

    # until the QTI exporter is fixed I have no way of knowing what to do with this
    # there is no apparent location to indicate left-side shuffling
    # potentially I could shuffle the actual pairs before rendering them
    # that's not really what this should be doing, though
    if shuffle:
        pass

    def add_answer(answer_text):
        answer_id = f"OPTION_{len(all_answers) + 1}"
        answer_el = SubElement(all_answers, "response_label", ident=answer_id)
        material = SubElement(answer_el, "material")
        SubElement(material, "mattext", texttype="text/plain").text = answer_text
        return answer_id

    for idx, p in enumerate(question["pairs"], start=1):
        pair = p["pair"]
        answer_id = add_answer(pair["right"])
        pair_id = f"response_{answer_id}"
        response_lid = SubElement(
            presentation, "response_lid", ident=pair_id, rcardinality="Multiple"
        )
        material = SubElement(response_lid, "material")
        SubElement(material, "mattext", texttype="text/plain").text = pair["left"]

        respcondition = SubElement(resprocessing, "respcondition")
        conditionvar = SubElement(respcondition, "conditionvar")
        SubElement(conditionvar, "varequal", respident=pair_id).text = answer_id
        SubElement(respcondition, "setvar", action="Add", varname="SCORE").text = (
            pair_score
        )

    # master list should have all categorized answers in it
    # just have to add distractors
    if "distractors" in question:
        for distractor in question["distractors"]:
            add_answer(distractor)

    # the right-side options are always shuffled
    # temporarily recreate the full list of answer choices
    temp_answers = Element("render_choice")
    # determine how many times we need to go through the full list of answers
    num_steps = len(all_answers)
    for i in range(num_steps):
        # choose a random answer, copy it into the temporary element
        rand = random.randint(0, len(all_answers) - 1)
        target = all_answers[rand]
        temp_answers.insert(i, copy.deepcopy(target))
        # remove it from the original so we don't get any duplicates by accident
        all_answers.remove(target)

    # original should be empty, replace it with the shuffled tree
    all_answers = temp_answers

    pair_elements = presentation.findall("response_lid")
    for pair_element in pair_elements:
        pair_element.append(copy.deepcopy(all_answers))

    return item
