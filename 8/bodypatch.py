from mitmproxy import ctx, http, exceptions
from mitmproxy.addonmanager import Loader
import json
from jsonpatch import JsonPatch, InvalidJsonPatch
from jsonpointer import JsonPointerException
import re

def load_patch(patch_file: str) -> JsonPatch:
    ctx.log.info(f'BodyPatch load file: {patch_file}')
    try:
        with open(patch_file, 'rt') as f:
            patch_data = json.load(f)
            ctx.log.info(f'BodyPatch data: {patch_data}')
            return JsonPatch(patch_data)
    except FileNotFoundError as err:
        ctx.log.warn(f'BodyPatch file: {patch_file} not found')
        return None
    except InvalidJsonPatch as err:
        ctx.log.warn(f'BodyPatch data not valid: {err}')
        return None

class BodyPatch():
    def __init__(self):
        self.patch = None
        self.path = None

    def load(self, loader: Loader) -> None:
        loader.add_option(name = 'bodypatch_file',
                          typespec = str,
                          default = '',
                          help = 'File that contains Json patch to apply')
        loader.add_option(name = 'bodypatch_request_path',
                          typespec = str,
                          default = '.*',
                          help = 'Pattern for matching request URLs to patch')

    def configure(self, updated: set[str]) -> None:
        if 'bodypatch_file' in updated:
            self.patch = load_patch(ctx.options.bodypatch_file)

        if 'bodypatch_request_path' in updated:
            try:
                self.path = re.compile(ctx.options.bodypatch_request_path)
                ctx.log.info(f'BodyPatch path: {self.path.pattern}')
            except re.error as err:
                raise exceptions.OptionsError(f'{err.msg}')

    def response(self, flow: http.HTTPFlow) -> None:
        if self.patch and self.path and self.path.match(flow.request.pretty_url):
            content_type = flow.response.headers.get('content-type')

            if content_type and content_type.find('application/json') != -1:
                ctx.log.info(f'BodyPatch patching: {flow.request.pretty_url}')
                data = json.loads(flow.response.get_text())

                try:
                    data = self.patch.apply(data)
                    flow.response.text = json.dumps(data)
                except JsonPointerException as err:
                    ctx.log.warn(f'BodyPatch: {err}')
            else:
                ctx.log.warn(f'BodyPatch: Not patching, content type is {content_type}')

addons = [BodyPatch()]
