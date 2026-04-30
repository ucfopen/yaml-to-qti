from lxml.etree import SubElement


def convert_file_upload_to_qti(item, question):
    presentation = item.find("presentation")
    presentation.set("allowed_types", question["allowed_extensions"])
    presentation.set("files_count", str(question["number_files"]))

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

    return item
