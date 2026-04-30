import re
import string

import latex2mathml.converter
import markdown


def convert_latex(source_text):
    if not source_text:
        return ""
    final_text = source_text

    # currently using '<latex> ... </latex>' as a pattern for identifying LaTeX blocks
    latex_search = r"<latex>(.*?)<(\/|\\)latex>"

    # iterate through the text and find all LaTeX blocks
    for latex in re.finditer(latex_search, source_text, re.DOTALL):
        original = latex.group(0)
        raw_latex = latex.group(1)
        # translated_latex = latex_to_canvas_img(raw_latex)
        translated_latex = latex2mathml.converter.convert(raw_latex)
        final_text = final_text.replace(original, translated_latex)

    return final_text


def sanitize_html(source_text):
    if not source_text:
        return ""
    # create a single string representing all 'safe' characters that we want to leave alone
    # this seems pretty naive and prone to error, ideally we'd know for sure what the
    #  criteria are for QTI imports to work reliably
    safe_chars = string.ascii_letters + string.digits + "%&#=-_\\/;.()[]{}<>?'\": "
    result = []

    for c in source_text:
        if c in safe_chars or c == "\n":
            # ignore the majority of characters and line breaks
            result.append(c)
        # commenting this out since the XML prettify/write process seems to handle it for us
        # kind of annoying, though - see if we can prevent that and be more intentional about this?
        # elif c in ['<', '>']:
        #     # handle HTML reserved characters specifically
        #     result.append(html.escape(c))
        else:
            # replace anything else with the character's hex code
            result.append(f"&#x{ord(c):X};")

    return "".join(result)


def sanitize_text_for_import(source_text):
    if not source_text:
        return ""
    text_with_mathml = convert_latex(source_text)
    html_text = markdown.markdown(text_with_mathml)
    return html_text
    # return sanitize_html(html_text)
