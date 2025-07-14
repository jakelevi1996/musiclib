import os
from jutility import util, plotting

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYLIST_DIR = os.path.join(CURRENT_DIR, "playlists")
PLAYLIST_INFO_DIR = os.path.join(CURRENT_DIR, "playlist_info")
MUSIC_ROOT_DIR = os.path.expanduser("~/Music")
IGNORE_STR = "bmp cue jpe jpg log m3u nfo pdf png txt"
IGNORE_EXTS = [("." + s) for s in IGNORE_STR.split()]
IGNORE_DIRS = ["..", "Voice Recorder", "d1f"]

def main():
    config = util.load_json("config.json")
    album_list  = sorted(Album(**d) for d in config)
    playlists = sorted(set(p for a in album_list for p in a.playlists))
    playlist_dict = {
        playlist: [
            album
            for album in album_list
            if  album.in_playlist(playlist)
        ]
        for playlist in playlists
    }

    make_readme(album_list, playlists, playlist_dict)

    make_all_album_list(album_list)

    make_histogram(album_list)

    make_playlists(album_list, playlist_dict)

def make_readme(
    album_list:     "list[Album]",
    playlists:      "list[str]",
    playlist_dict:  "dict[str, list[Album]]",
):
    printer = util.Printer("README", ".", "md", print_to_console=False)
    printer("# musiclib")
    printer("\n![](img/Albums_by_year.png)")

    num_albums = len(album_list)

    printer("\n## Contents\n")
    for i, playlist in enumerate(playlists + ["All albums"], start=1):
        link_str = playlist.lower().replace(" ", "-")
        if playlist in playlist_dict:
            playlist = "%s (%i)" % (playlist, len(playlist_dict[playlist]))
        if playlist == "All albums":
            playlist = "%s (%i)" % (playlist, len(album_list))

        printer("%i. [%s](#%s)" % (i, playlist, link_str))

    for playlist in playlists:
        printer("\n## %s\n" % playlist)
        for album in playlist_dict[playlist]:
            printer("- %s" % album.name)

    printer("\n## All albums\n")
    for album in album_list:
        printer("- %s" % album.name)

def make_all_album_list(album_list: "list[Album]"):
    util.save_text("\n".join(a.name for a in album_list), "albums", ".")

def make_histogram(album_list: "list[Album]"):
    years  = [album.get_year() for album in album_list]
    x = list(range(min(years), max(years) + 1))
    plotting.plot(
        plotting.Hist(years, x, ec=None),
        xlabel="Year",
        ylabel="Count",
        figsize=[6, 4],
        plot_name="Albums by year",
        dir_name="img",
    )

def make_playlists(
    album_list:     "list[Album]",
    playlist_dict:  "dict[str, list[Album]]",
):
    album_names = set(a.name for a in album_list)

    music_dirs = set(
        os.path.join(root, d)
        for root, dirs, files in os.walk(MUSIC_ROOT_DIR)
        for d in dirs
    )
    album_to_dir = {
        os.path.basename(d): d
        for d in music_dirs
        if os.path.basename(d) in album_names
    }

    missing_albums = album_names - set(album_to_dir.keys())
    if len(missing_albums) > 0:
        raise RuntimeError(
            "The following albums could not be found on disk: %s"
            % ", ".join(sorted(missing_albums))
        )

    album_to_files = {
        a: sorted(get_files_in_dir(d))
        for a, d in album_to_dir.items()
    }

    indexed_files = set(f for a in album_to_files.values() for f in a)
    all_files = set(get_files_in_dir(MUSIC_ROOT_DIR))
    missing_files = [
        f
        for f in (all_files - indexed_files)
        if os.path.basename(os.path.dirname(f)) not in IGNORE_DIRS
    ]
    if len(missing_files) > 0:
        raise RuntimeError(
            "The following files could not be found in `config.json`:\n\n%s"
            % "\n".join(sorted(missing_files))
        )

    for playlist, album_list in playlist_dict.items():
        m3u_printer = util.Printer(
            playlist,
            PLAYLIST_DIR,
            "m3u",
            print_to_console=False,
        )
        for album in album_list:
            m3u_printer(*album_to_files[album.name], sep="\n")

        info_printer = util.Printer(
            playlist,
            PLAYLIST_INFO_DIR,
            print_to_console=False,
        )
        included_album_names = set(a.name for a in album_list)
        excluded_album_names = album_names - included_album_names
        info_printer("Albums in playlist:")
        info_printer(*sorted(included_album_names), sep="\n")
        info_printer.hline()
        info_printer("Albums NOT in playlist:")
        info_printer(*sorted(excluded_album_names), sep="\n")

def get_files_in_dir(dir_name: str) -> list[str]:
    return [
        os.path.relpath(
            os.path.join(root, f),
            os.path.join(MUSIC_ROOT_DIR, "playlists"),
        )
        for root, dirs, files in os.walk(dir_name)
        for f in files
        if not is_ignored(f)
    ]

def is_ignored(full_path: str) -> bool:
    _, ext = os.path.splitext(full_path)
    return ext.lower() in IGNORE_EXTS

class Album:
    def __init__(
        self,
        name:       str,
        playlists:  list[str],
    ):
        assert isinstance(name, str)
        assert isinstance(playlists, list)
        assert len(name) > 0
        assert len(playlists) > 0

        self.name = name
        self.playlists = playlists

    def in_playlist(self, playlist: str) -> bool:
        return (playlist in self.playlists)

    def get_year(self) -> int:
        return int(self.name[:4])

    def __lt__(self, other: "Album"):
        return self.name < other.name

    def __repr__(self):
        return "Album(%s)" % self.name

if __name__ == "__main__":
    with util.Timer("main"):
        main()
