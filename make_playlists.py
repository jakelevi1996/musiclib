import os
from jutility import util
from make_readme import Album

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYLIST_DIR = os.path.join(CURRENT_DIR, "playlists")

def main():
    config = util.load_json("config.json")
    album_list = [Album(**d) for d in config]
    album_dict = {a.name: a for a in album_list}
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
        os.path.relpath(os.path.join(root, d), music_root_dir)
        for root, dirs, files in os.walk(music_root_dir)
        for d in dirs
    )
    dir_to_album = {
        d: album_dict[os.path.basename(d)].name
        for d in music_dirs
        if os.path.basename(d) in album_dict
    }
    album_to_dir = {a: d for d, a in dir_to_album.items()}

    missing_albums = set(album_dict.keys()) - set(album_to_dir.keys())
    if len(missing_albums) > 0:
        raise RuntimeError(
            "The following albums could not be found on disk: %s"
            % ", ".join(sorted(missing_albums))
        )

    album_to_files = {
        a: sorted(
            os.path.relpath(
                os.path.join(music_root_dir, d, f),
                music_root_dir,
            )
            for root, dirs, files in os.walk(os.path.join(music_root_dir, d))
            for f in files
        )
        for a, d in album_to_dir.items()
    }

    for playlist, album_list in playlist_dict.items():
        m3u_printer = util.Printer(
            playlist,
            PLAYLIST_DIR,
            "m3u",
            print_to_console=False,
        )
        for album in album_list:
            m3u_printer(*album_to_files[album.name], sep="\n")

if __name__ == "__main__":
    with util.Timer("main"):
        main()
