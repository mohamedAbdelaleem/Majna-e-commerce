import json
from rest_framework.parsers import MultiPartParser, DataAndFiles


class MultipartJsonParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream, media_type=media_type, parser_context=parser_context)
        data = {}
        # parse non-files attributes
        for key, value in result.data.items():
            if isinstance(value, str) and ('{' in value or '[' in value):
                try:
                    value = value.replace("'", "\"")
                    data[key] = json.loads(value)
                except ValueError as err:
                    print(err)
                    data[key] = value
            else:
                data[key] = value
        # add files to album
        for item in data["album"]:
            item["image"] = result.files[item["image"]]

        return DataAndFiles(data, result.files)

