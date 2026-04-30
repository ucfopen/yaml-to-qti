from lxml.etree import SubElement


def percent_range(target_number, margin_percent):
    percentage_value = (margin_percent / 100) * target_number
    lower_limit = target_number - percentage_value
    upper_limit = target_number + percentage_value

    return lower_limit, upper_limit


def absolute_range(target_number, margin_value):
    lower_limit = target_number - margin_value
    upper_limit = target_number + margin_value

    return lower_limit, upper_limit


def precision_significant(target_number, precision):
    # if the first significant digit is on the left side of the decimal
    #  point, we'll have to account for it when determining the position
    #  of other characters
    character_count = precision + 1 if target_number > 1 else precision
    # identify where the significant figures begin in the given number
    n = str(target_number)
    first_nonzero = 0
    for i in range(len(n)):
        if n[i] not in ["0", "."]:
            first_nonzero = i
            break

    # make sure the necessary number of significant digits are present
    sig = n[first_nonzero:].ljust(int(character_count), "0")
    sig = n[0:first_nonzero] + sig

    # generate a number that can be added to/subtracted from the
    #  target number in order to generate lower/upper limits that
    #  round towards the target number
    decimal_part = sig.split(".")[1]
    modifier = "0." + ("0" * len(decimal_part)) + "5"

    lower_limit = target_number - float(modifier)
    upper_limit = target_number + float(modifier)

    lower_limit = round(lower_limit, int(character_count) + first_nonzero)
    upper_limit = round(upper_limit, int(character_count) + first_nonzero)

    return lower_limit, upper_limit


def precision_decimal(target_number, precision):
    # make sure the target number has the necessary number of decimal places
    actual_target = f"{target_number:.{int(precision)}f}"
    # generate a number that can be added to/subtracted from the
    #  target number in order to generate lower/upper limits that
    #  round towards the target number
    decimal_part = actual_target.split(".")[1]
    modifier = "0." + ("0" * len(decimal_part)) + "5"

    lower_limit = target_number - float(modifier)
    upper_limit = target_number + float(modifier)

    lower_limit = round(lower_limit, int(precision) + 1)
    upper_limit = round(upper_limit, int(precision) + 1)

    return lower_limit, upper_limit


def convert_numerical_to_qti(item, question):
    presentation = item.find("presentation")
    response_id = f"RESPONSE_{question['id']}"

    response_str = SubElement(
        presentation, "response_str", ident=response_id, rcardinality="Single"
    )
    render_fib = SubElement(response_str, "render_fib", fibtype="Decimal", prompt="Box")
    SubElement(render_fib, "response_label", ident="answer")

    # Add resprocessing
    resprocessing = SubElement(item, "resprocessing")
    outcomes = SubElement(resprocessing, "outcomes")
    SubElement(
        outcomes,
        "decvar",
        {
            "maxvalue": str(question["points"]),
            "minvalue": "0",
            "varname": "SCORE",
            "vartype": "Decimal",
        },
    )

    respcondition_correct = SubElement(
        resprocessing, "respcondition", **{"continue": "No"}
    )
    conditionvar_correct = SubElement(respcondition_correct, "conditionvar")

    parent_or = SubElement(conditionvar_correct, "or")

    # depending on whether the answer accepts a margin of error there will be
    #  different information attached to the resulting XML
    range_function = None

    # not every answer option will have a 'varequal' tag, but assume we'll make one
    render_varequal = True
    # the attributes of that tag will be different depending on the answer type
    varequal_props = {}

    # most answer types will also require the lower/upper limits to be explicit
    lower_limit = None
    upper_limit = None

    question_answer = question["answer"]

    # check for margins first
    if "margin_type" in question_answer:
        margin_type = question_answer["margin_type"]
        varequal_props["margin"] = str(question_answer["tolerance"])
        varequal_props["margintype"] = margin_type
        # varequal.set("margin", str(question_answer["tolerance"]))
        # varequal.set("margintype", margin_type)
        if margin_type == "percent":
            range_function = percent_range
        elif margin_type == "absolute":
            range_function = absolute_range
        else:
            raise Exception(f"Unknown margin type in {question["id"]}: {margin_type}")
    # then check for precision
    elif "precision_type" in question_answer:
        varequal_props["precision"] = str(question_answer["precision"])
        if question_answer["precision_type"] == "significant_digits":
            varequal_props["precisiontype"] = "significantDigits"
            range_function = precision_significant
        elif question_answer["precision_type"] == "decimals":
            varequal_props["precisiontype"] = "decimals"
            range_function = precision_decimal
        else:
            raise Exception(
                f"Unknown precision type in {question["id"]}: {question_answer["precision_type"]}"
            )
        pass
    # then check for a range
    elif "range_start" in question_answer and "range_end" in question_answer:
        render_varequal = False
        lower_limit = question_answer["range_start"]
        upper_limit = question_answer["range_end"]
    # default to exact answers
    else:
        lower_limit = upper_limit = float(question_answer["value"])

    if render_varequal:
        SubElement(
            parent_or, "varequal", respident=response_id, **varequal_props
        ).text = str(question_answer["value"])

    # explicitly define the lower/upper limits of 'correct' for safety if they aren't already
    if not lower_limit or not upper_limit:
        target_modifier = ""
        if "tolerance" in question_answer:
            target_modifier = question_answer["tolerance"]
        elif "precision" in question_answer:
            target_modifier = question_answer["precision"]
        else:
            raise Exception(
                f"Required 'tolerance' or 'precision' key missing in {question["id"]} answer definition"
            )
        lower_limit, upper_limit = range_function(
            float(question_answer["value"]), float(target_modifier)
        )
    parent_and = SubElement(parent_or, "and")

    # precision-based answers are not inclusive of the limits, margin-based answers are
    # this is to account for rounding up/down of decimal places
    exclusive = "precision" in question_answer
    SubElement(
        parent_and, "vargt" if exclusive else "vargte", respident=response_id
    ).text = str(lower_limit)
    SubElement(
        # TODO: this seems to be buggy behavior in the QTI importer
        # this should probably be an "lt" tag in the event of a precision answer in order to
        #  account for rounding down - but the QTI importer fails to import questions
        #  unless this is an "lte" tag, at least that's what it looks like
        parent_and,
        "varlte" if exclusive else "varlte",
        respident=response_id,
    ).text = str(upper_limit)

    SubElement(respcondition_correct, "setvar", varname="SCORE", action="Set").text = (
        str(question["points"])
    )
    SubElement(
        respcondition_correct,
        "displayfeedback",
        feedbacktype="Response",
        linkrefid="correct",
    )

    return item
