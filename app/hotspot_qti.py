from lxml.etree import SubElement

from app.string_utils import sanitize_text_for_import


def convert_hotspot_to_qti(item, question):
    presentation = item.find("presentation")
    response_id = f"QUESTION_{question['id']}"

    flow = SubElement(presentation, "flow")
    response_xy = SubElement(
        flow, "response_xy", ident=response_id, rcardinality="Multiple", rtiming="No"
    )
    text_material = SubElement(response_xy, "material")
    SubElement(text_material, "mattext", texttype="text/html").text = (
        sanitize_text_for_import(question["text"])
    )
    render_hotspot = SubElement(response_xy, "render_hotspot")
    figure_path_parts = question["figure"].split("/")
    filename = figure_path_parts[-1]
    image_material = SubElement(render_hotspot, "material")
    SubElement(image_material, "matimage", uri=f"$IMS-CC-FILEBASE$/media/{filename}")

    for i, a in enumerate(question["areas"], start=1):
        area = a["area"]

        SubElement(
            render_hotspot, "response_label", ident=str(i), rarea=area["type"]
        ).text = ",".join(map(str, area["locations"]))

    return item
