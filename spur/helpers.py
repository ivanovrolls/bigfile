from pathlib import Path

ROOT_MARKERS = ("composer.json", ".git")


def to_project_relative(file: Path, root: Path) -> str:
    root = root.resolve()  # resolve project root as absolute
    file = file.resolve().relative_to(root)  # make file relative to resolve root
    file_path_str = file.as_posix()  # make file a forwardslash str
    return file_path_str


def find_project_root(start: Path) -> Path:
    """walk up from where you are, never reaching home or /
    take first .spur found before leaving repo
    otherwise take nearest composer.json or .git.
    otherwise use where you are"""

    start = start.resolve()

    # ensuring a stray marker in a home folder doesnt swallow every project beneath
    stop_at = {
        Path.home().resolve(),
        Path(start.anchor),
    }  # dont look for any marker above here
    candidates = []
    for directory in [
        start,
        *start.parents,
    ]:  # start parents is all the directories above start
        if directory in stop_at:
            break  # ensure candidates where .spur should not exist are not looked at
        candidates.append(directory)

    # look for a .spur marker but never above repo root
    for directory in candidates:
        if (
            directory / ".spur"
        ).is_dir():  # the / builds the path to the possible marker file
            return directory
        if (directory / ".git").exists():
            break

    # fall back to nearest project marker
    for directory in candidates:
        for marker in ROOT_MARKERS:
            if (directory / marker).exists():
                return directory

    # if none found, just use this start path
    return start
