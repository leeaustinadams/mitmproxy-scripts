# mitmproxy-scripts #
A collection of scripts for [mitmproxy](https://mitmproxy.org)

# scripts #
[BodyPatch](8/bodypatch.py) - Use [JsonPatch](https://github.com/stefankoegl/python-json-patch) to patch json response bodies

# examples #

[BodyPatch](examples/patch.json)

	$ mitmproxy --listen-port 8888 -s ./8/bodypatch.py --set "bodypatch_file=./samples/patch.json" --set "bodypatch_request_path=http://host/path/data.json"
