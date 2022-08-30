import common_utils
import json
import base64
import sys

BASE_HTML = """
<!DOCTYPE html>
<html>
<body>

<div class="container">
    <br/>


    <table class="linkelement" border="1px" cellpadding="10px">
        __text__
    </table>

</div>
<script  type="text/javascript">
    function copyTextValue(textValue) {
        var elementHandle = document.getElementById("inputHolder");
        elementHandle.value = textValue;
        elementHandle.select();
        elementHandle.setSelectionRange(0, 99999)
        document.execCommand("copy");
        elementHandle.value = "";
    }

    function copyPasswordOld(encryptedPass) {
        var elementHandle = document.getElementById("inputHolder");
        elementHandle.value = atob(encryptedPass);
        elementHandle.select();
        elementHandle.setSelectionRange(0, 99999)
        document.execCommand("copy");
        elementHandle.value = "";
    }

    function copyPassword(text) {
        elem = document.createElement('textarea');
        elem.value = atob(text);
        document.body.appendChild(elem);
        elem.select();
        document.execCommand('copy');
        document.body.removeChild(elem);
    }
</script>

<style type="text/css">
    .container {
        text-align: center;
    }
    .linkelement {
        display: inline-block;
    }
</style>
</body>
</html>
"""


def build_sub_item(subitem):
    if 'encrypted' in subitem:
        return "  <button onclick=\"copyPassword('{0}')\">{1}</button>".format(subitem['encrypted'].encode(), subitem['label'])
    else:
        encoded_string = base64.b64encode(subitem['content'].encode("utf-8")).decode()
        return "  <button onclick=\"copyPassword('{0}')\">{1}</button>".format(encoded_string, subitem['label'])

def build_content_line(content_line):
    html = ""
    for subItem in content_line['subItems']:
        html = html + build_sub_item(subItem)

    table_row_text = "<tr><td>__text__</td></tr><br/><br/>"
    replace_char = "__text__"
    return table_row_text.replace(replace_char, html)

def convert_to_html(json_content):
    html = ""
    for content_line in json_content["items"]:
        html = html + build_content_line(content_line)

    replace_char = "__text__"
    return BASE_HTML.replace(replace_char, html)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python file <input-cred-file> <output-html-file>")
    file_content = common_utils.read_file_contents(sys.argv[1])
    json_content = json.loads(file_content)
    html = convert_to_html(json_content)
    common_utils.write_to_file(sys.argv[2], html)
    print(html)