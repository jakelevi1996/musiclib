from jutility import util

def main():
    config = util.load_json("config.json")
    album_list  = sorted(Album(**d) for d in config)
    playlists = sorted(set(p for a in album_list for p in a.playlists))
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
    for playlist in ["Contents"] + playlists + ["All albums"]:
        link_str = playlist.lower().replace(" ", "-")
        if playlist in playlist_dict:
            playlist = "%s (%i)" % (playlist, len(playlist_dict[playlist]))
        if playlist == "All albums":
            playlist = "%s (%i)" % (playlist, len(album_list))

        printer("- [%s](#%s)" % (playlist, link_str))

    for playlist in playlists:
        printer("\n## %s\n" % playlist)
        for album in playlist_dict[playlist]:
            printer("- %s" % album.name)

    printer("\n## All albums\n")
    for album in album_list:
        printer("- %s" % album.name)

    util.save_text("\n".join(a.name for a in album_list), "albums", ".")

class Album:
    def __init__(
        self,
        name: str,
        playlists: list[str],
    ):
        assert isinstance(name, str)
        assert isinstance(playlists, list)
        assert len(name) > 0
        assert len(playlists) > 0

        self.name = name
        self.playlists = playlists

    def in_playlist(self, playlist):
        return (playlist in self.playlists)

    def __lt__(self, other: "Album"):
        return self.name < other.name

    def __repr__(self):
        return "Album(%s)" % self.name

if __name__ == "__main__":
    with util.Timer("main"):
        main()
