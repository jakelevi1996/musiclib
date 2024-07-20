from jutility import util

def main():
    config = util.load_json("config.json")
    album_list  = sorted([Album(d) for d in config], key=lambda a: a.name)
    playlists = sorted(set(p for a in album_list for p in a.get_playlists()))
    playlist_dict = {
        playlist: [
            album for album in album_list
            if album.in_playlist(playlist)
        ]
        for playlist in playlists
    }

    printer = util.Printer("README", ".", "md", print_to_console=False)
    printer("# musiclib")

    num_albums = len(album_list)

    printer("\n## Contents\n")
    for playlist in ["Contents"] + playlists + ["All playlists"]:
        link_str = playlist.lower().replace(" ", "-")
        if playlist in playlist_dict:
            playlist = "%s (%i)" % (playlist, len(playlist_dict[playlist]))
        if playlist == "All playlists":
            playlist = "%s (%i)" % (playlist, len(album_list))

        printer("- [%s](#%s)" % (playlist, link_str))

    for playlist in playlists:
        printer("\n## %s\n" % playlist)
        for album in playlist_dict[playlist]:
            album.print(printer)

    printer("\n## All playlists\n")
    for album in album_list:
        album.print(printer)

    util.save_text("\n".join(a.name for a in album_list), "albums", ".")

class Album:
    def __init__(self, album_config):
        self.config = album_config

        assert self.is_valid_key("name", str)
        assert self.is_valid_key("playlists", list)

        self.name = album_config["name"]

    def is_valid_key(self, key, dtype=str):
        return (
            (key in self.config)
            and (self.config[key] is not None)
            and (isinstance(self.config[key], dtype))
            and (len(self.config[key]) > 0)
        )

    def print(self, printer):
        printer("- %s" % self.name)
        printer(
            "  - Playlists: %s"
            % ", ".join(sorted(self.config["playlists"]))
        )

    def get_playlists(self):
        return self.config["playlists"]

    def in_playlist(self, playlist):
        return (playlist in self.config["playlists"])

    def __repr__(self):
        return "Album(%s)" % self.name

if __name__ == "__main__":
    with util.Timer("main"):
        main()
