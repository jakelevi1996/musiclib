import os
from jutility import util
from make_readme import Album

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYLIST_DIR = os.path.join(CURRENT_DIR, "playlists")
PLAYLIST_INFO_DIR = os.path.join(CURRENT_DIR, "playlist_info")
IGNORE_EXTS = [
    ".bmp",
    ".cue",
    ".jpeg",
    ".jpg",
    ".log",
    ".m3u",
    ".nfo",
    ".pdf",
    ".png",
    ".txt",
]

def main():
    config = util.load_json("config.json")
    album_list = [Album(**d) for d in config]
    album_names = set(a.name for a in album_list)
    playlists = set(playlist for a in album_list for playlist in a.playlists)
    playlist_dict = {
        playlist: sorted(
            album for album in album_list
            if album.in_playlist(playlist)
        )
        for playlist in playlists
    }

    music_root_dir = os.path.expanduser("~/Music")

    music_dirs = set(
        os.path.join(root, d)
        for root, dirs, files in os.walk(music_root_dir)
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
        a: sorted(
            os.path.relpath(
                os.path.join(root, f),
                os.path.join(music_root_dir, "playlists"),
            )
            for root, dirs, files in os.walk(d)
            for f in files
            if os.path.splitext(f)[-1].lower() not in IGNORE_EXTS
        )
        for a, d in album_to_dir.items()
    }

    file_exts = set(
        os.path.splitext(f)[-1]
        for f_list in album_to_files.values()
        for f in f_list
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

if __name__ == "__main__":
    with util.Timer("main"):
        main()
