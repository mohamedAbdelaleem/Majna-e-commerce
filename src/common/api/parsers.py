import json
from rest_framework.parsers import MultiPartParser, DataAndFiles
from rest_framework.exceptions import ValidationError


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
        if "album" not in data:
            raise ValidationError("Missing album")
        for item in data["album"]:
            image_key = item["image"]
            if image_key not in result.files:
                raise ValidationError(f"{image_key} file missing!")
            item["image"] = result.files[image_key]

        return DataAndFiles(data, result.files)

