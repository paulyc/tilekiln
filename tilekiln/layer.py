from tilekiln.definition import Definition


class Layer:
    '''A layer in the tileset

    A Layer contains all the information needed to say what the definitions
    are for every zoom
    '''
    def __init__(self, id, layer_config, fs):
        self.id = id
        self.description = layer_config.get("description")
        self.fields = layer_config.get("fields")

        self.definitions = []

        self.geometry = set(layer_config.get("geometry", []))

        if "sql" in layer_config:
            for d in layer_config["sql"]:
                self.definitions.append(Definition(self.id,
                                        fs.readtext(d["file"]),
                                        d["minzoom"], d["maxzoom"],
                                        d.get("extent")))

            self.minzoom = min([d.minzoom for d in self.definitions])
            self.maxzoom = max([d.maxzoom for d in self.definitions])

    def __eq__(self, other):
        return (self.id == other.id and self.description == other.description
                and self.fields == other.fields
                and self.definitions == other.definitions
                and self.geometry == other.geometry)

    def definition_for_zoom(self, zoom):
        ''' Get the right definition for a given zoom
        '''
        for d in self.definitions:
            if zoom >= d.minzoom and zoom <= d.maxzoom:
                return d

    def render_tile(self, tile, db):
        d = self.definition_for_zoom(tile[0])
        if d is None:
            return None

        return db.generate_tilelayer(d, tile)
