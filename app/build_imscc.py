import os
import shutil
from datetime import datetime
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, ElementTree, SubElement


def make_child_node_with_text(element, node_text):
    element.text = node_text


def build_imscc(image_folder, output_folder):
    # Create IMSCC structure
    os.makedirs(output_folder, exist_ok=True)

    # Handle images only if image_folder is not None
    if image_folder is not None:
        media_folder = os.path.join(output_folder, "media")
        os.makedirs(media_folder, exist_ok=True)
        try:
            for image_file in os.listdir(image_folder):
                shutil.copy(os.path.join(image_folder, image_file), media_folder)
        except IsADirectoryError:
            raise Exception(
                "Found a subfolder when trying to copy associated media from provided .zip file."
            )

    # Add imsmanifest.xml
    manifest_path = os.path.join(output_folder, "imsmanifest.xml")
    manifest = ElementTree(
        Element(
            "manifest",
            {
                "identifier": "MANIFEST01",
                "xmlns": "http://www.imsglobal.org/xsd/imscp_v1p1",
                "xmlns:lom": "http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource",
                "xmlns:imsmd": "http://www.imsglobal.org/xsd/imsmd_v1p2",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd",  # noqa: E501
            },
        )
    )

    organizations = SubElement(manifest.getroot(), "organizations")
    SubElement(organizations, "organization", {"identifier": "ORG01"})

    metadata = SubElement(manifest.getroot(), "metadata")
    make_child_node_with_text(SubElement(metadata, "schema"), "IMS Content")
    make_child_node_with_text(SubElement(metadata, "schemaversion"), "1.1.3")
    imsmd_lom = SubElement(metadata, "imsmd:lom")
    imsmd_general = SubElement(imsmd_lom, "imsmd:general")
    imsmd_title = SubElement(imsmd_general, "imsmd:title")
    make_child_node_with_text(
        SubElement(imsmd_title, "imsmd:string"), "Testing AI-Generated QTI Import"
    )
    imsmd_lifecycle = SubElement(imsmd_lom, "imsmd:lifeCycle")
    imsmd_contribute = SubElement(imsmd_lifecycle, "imsmd:contribute")
    imsmd_date = SubElement(imsmd_contribute, "imsmd:date")
    make_child_node_with_text(
        SubElement(imsmd_date, "imsmd:dateTime"), datetime.now().strftime("%Y-%m-%d")
    )
    imsmd_rights = SubElement(imsmd_lom, "imsmd:rights")
    imsmd_copyright_etc = SubElement(
        imsmd_rights, "imsmd:copyrightAndOtherRestrictions"
    )
    make_child_node_with_text(SubElement(imsmd_copyright_etc, "imsmd:value"), "yes")
    imsmd_description = SubElement(imsmd_rights, "imsmd:description")
    make_child_node_with_text(
        SubElement(imsmd_description, "imsmd:string"),
        "Private (Copyrighted) - http://en.wikipedia.org/wiki/Copyright",
    )

    resources = SubElement(manifest.getroot(), "resources")

    # Add QTI file as a resource
    qti_resource = SubElement(
        resources,
        "resource",
        {"identifier": "qti", "type": "imsqti_xmlv1p2", "href": "qti/qti.xml"},
    )
    SubElement(qti_resource, "file", {"href": "qti/qti.xml"})

    # Add each image as a separate resource only if image_folder is not None
    if image_folder is not None:
        for image_file in os.listdir(media_folder):
            image_resource = SubElement(
                resources,
                "resource",
                {
                    "identifier": os.path.splitext(image_file)[0],
                    "type": "webcontent",
                    "href": f"media/{image_file}",
                },
            )
            SubElement(image_resource, "file", {"href": f"media/{image_file}"})

    # Write manifest to file
    ElementTree(manifest.getroot()).write(
        manifest_path, encoding="utf-8", xml_declaration=True
    )
    with open(manifest_path, "r", encoding="utf-8") as file:
        raw_content = file.read()
    pretty_manifest = parseString(raw_content).toprettyxml(indent="  ")
    with open(manifest_path, "w", encoding="utf-8") as file:
        file.write(pretty_manifest)

    print(f"IMSCC package created successfully in '{output_folder}'.")


if __name__ == "__main__":
    image_folder = input(
        "Enter the path to the image folder (or 'n' if not needed): "
    ).strip()
    if image_folder.lower() == "n":
        image_folder = None
    output_folder = input("Enter the output folder for the IMSCC package: ").strip()

    build_imscc(image_folder, output_folder)
