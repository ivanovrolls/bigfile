from pathlib import Path

ROOT_MARKERS = ("composer.json", ".git")


def to_project_relative(file: Path, root: Path) -> str:
    root = root.resolve()  # resolve project root as absolute
    file = file.resolve().relative_to(root)  # make file relative to resolve root
    file_path_str = file.as_posix()  # make file a forwardslash str
    return file_path_str


def find_project_root(start: Path) -> Path:
    start = start.resolve()

    # look for a spur specific marker
    for directory in [start, *start.parents]:
        if (directory / ".spur").is_dir():
            return directory

    # look for a composer as a marker, or .git
    for directory in [start, *start.parents]:
        for marker in ROOT_MARKERS:
            if (directory / marker).exists():
                return directory

    # if none found, just use this start path
    return start
